import os
import sys
import re
from pypdf import PdfReader
from sqlalchemy.orm import Session
from datetime import datetime

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import User, Syllabus, StructuredTopic, SourceType, ContentStatus

PDF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Material de Estudio",
    "temarios",
    "Anexo_V_Arquitectos Técnicos.pdf"
)

def extract_text_from_pdf(pdf_path):
    print(f"📄 Reading PDF: {pdf_path}")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_syllabus_text(text):
    print("🔍 Parsing text...")
    
    # Normalize text: remove multiple spaces, handle newlines
    lines = text.split('\n')
    
    # Structure to hold the parsed data
    structure = {
        "comunes": [],
        "especificas": []
    }
    
    current_section = None
    current_topic_buffer = []
    current_topic_number = None
    
    # Regex for topic start: "1. ", "10. ", etc.
    topic_start_regex = re.compile(r'^(\d+)\.\s+(.*)')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect sections
        if "Programa de materias comunes" in line:
            current_section = "comunes"
            print("Found section: Comunes")
            continue
        elif "Programa de materias específicas" in line:
            # If we were building a topic, save it
            if current_topic_number is not None:
                topic_content = " ".join(current_topic_buffer).strip()
                structure["comunes"].append({
                    "number": current_topic_number,
                    "title": topic_content
                })
                current_topic_buffer = []
                current_topic_number = None
                
            current_section = "especificas"
            print("Found section: Específicas")
            continue
            
        # Skip header/footer noise if possible
        if "GOBIERNO DE ARAGON" in line or "Departamento de Hacienda" in line or "ANEXO V" in line:
            continue
            
        # Check for topic start
        match = topic_start_regex.match(line)
        if match:
            # Save previous topic if exists
            if current_topic_number is not None:
                topic_content = " ".join(current_topic_buffer).strip()
                if current_section:
                    structure[current_section].append({
                        "number": current_topic_number,
                        "title": topic_content
                    })
            
            # Start new topic
            current_topic_number = int(match.group(1))
            current_topic_buffer = [match.group(2)]
        else:
            # Continuation of previous topic
            if current_topic_number is not None:
                current_topic_buffer.append(line)
    
    # Save last topic
    if current_topic_number is not None and current_section:
        topic_content = " ".join(current_topic_buffer).strip()
        structure[current_section].append({
            "number": current_topic_number,
            "title": topic_content
        })
        
    return structure

def get_target_user(db):
    user = db.query(User).filter(User.username == "alejandro").first()
    if not user:
        print("User 'alejandro' not found, trying to find any user...")
        user = db.query(User).first()
    return user

def setup_syllabus(db, user, structure):
    syllabus_name = "Arquitectos Técnicos - Anexo V"
    existing_syllabus = db.query(Syllabus).filter(
        Syllabus.name == syllabus_name, 
        Syllabus.user_id == user.id
    ).first()
    
    if existing_syllabus:
        print(f"⚠️ Syllabus '{syllabus_name}' already exists. Deleting and recreating...")
        db.delete(existing_syllabus)
        db.commit()
        
    syllabus = Syllabus(
        user_id=user.id,
        name=syllabus_name,
        description="Temario oficial para Cuerpo de Funcionarios Técnicos, Escala Técnica Facultativa, Arquitectos Técnicos (Anexo V)",
        source_file="Anexo_V_Arquitectos Técnicos.pdf",
        total_topics=len(structure["comunes"]) + len(structure["especificas"])
    )
    db.add(syllabus)
    db.commit()
    db.refresh(syllabus)
    print(f"✅ Created Syllabus: {syllabus.name} (ID: {syllabus.id})")
    return syllabus

def create_topics(db, user, syllabus, structure):
    # --- Materias Comunes ---
    comunes_root = StructuredTopic(
        user_id=user.id,
        syllabus_id=syllabus.id,
        parent_id=None,
        order_index=1,
        level=0,
        title="Materias Comunes",
        code="C",
        content_status=ContentStatus.PARTIAL
    )
    db.add(comunes_root)
    db.commit()
    db.refresh(comunes_root)
    
    print(f"  Created Section: Materias Comunes ({len(structure['comunes'])} topics)")
    
    for topic in structure["comunes"]:
        t = StructuredTopic(
            user_id=user.id,
            syllabus_id=syllabus.id,
            parent_id=comunes_root.id,
            order_index=topic["number"],
            level=1,
            title=topic["title"],
            code=f"C.{topic['number']}",
            source_type=SourceType.NORMATIVA,
            content_status=ContentStatus.EMPTY
        )
        db.add(t)
    
    # --- Materias Específicas ---
    especificas_root = StructuredTopic(
        user_id=user.id,
        syllabus_id=syllabus.id,
        parent_id=None,
        order_index=2,
        level=0,
        title="Materias Específicas",
        code="E",
        content_status=ContentStatus.PARTIAL
    )
    db.add(especificas_root)
    db.commit()
    db.refresh(especificas_root)
    
    print(f"  Created Section: Materias Específicas ({len(structure['especificas'])} topics)")
    
    for topic in structure["especificas"]:
        t = StructuredTopic(
            user_id=user.id,
            syllabus_id=syllabus.id,
            parent_id=especificas_root.id,
            order_index=topic["number"],
            level=1,
            title=topic["title"],
            code=f"E.{topic['number']}",
            source_type=SourceType.NORMATIVA,
            content_status=ContentStatus.EMPTY
        )
        db.add(t)
        
    db.commit()

def import_to_db(structure):
    db = SessionLocal()
    try:
        user = get_target_user(db)
        if not user:
            print("❌ No users found in database. Please run seed scripts first.")
            return
        
        print(f"👤 Assigning to user: {user.username} (ID: {user.id})")
        
        syllabus = setup_syllabus(db, user, structure)
        create_topics(db, user, syllabus, structure)
        
        print("✅ Database import completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF file not found at: {PDF_PATH}")
    else:
        text = extract_text_from_pdf(PDF_PATH)
        parsed_structure = parse_syllabus_text(text)
        import_to_db(parsed_structure)