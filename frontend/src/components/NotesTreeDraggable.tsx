'use client';

import { useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

export interface NoteTreeNode {
  hierarchy_id: number;
  note_id: number;
  title: string;
  note_type: 'section' | 'content';
  is_featured: boolean;
  order_index: number;
  children: NoteTreeNode[];
}

interface SortableItemProps {
  node: NoteTreeNode;
  level: number;
  onSelectNote: (noteId: number) => void;
  selectedNoteId: number | null;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

function SortableItem({
  node,
  level,
  onSelectNote,
  selectedNoteId,
  isExpanded,
  onToggleExpand,
}: SortableItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: node.hierarchy_id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const hasChildren = node.children && node.children.length > 0;
  const isSection = node.note_type === 'section';
  const isSelected = selectedNoteId === node.note_id;

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      <div
        className={`
          flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer
          transition-colors duration-150
          ${isSelected
            ? 'bg-blue-500 text-white'
            : 'hover:bg-gray-100 dark:hover:bg-gray-800'
          }
        `}
        style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
      >
        {/* Drag Handle */}
        <button
          {...listeners}
          className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors cursor-grab active:cursor-grabbing"
          onClick={(e) => e.stopPropagation()}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 8h16M4 16h16"
            />
          </svg>
        </button>

        {/* Expand/Collapse */}
        {hasChildren && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleExpand();
            }}
            className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <svg
              className={`w-4 h-4 transition-transform duration-200 ${
                isExpanded ? 'transform rotate-90' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        )}

        {/* Icon */}
        <span className="flex-shrink-0">
          {isSection ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 7h18M3 12h18M3 17h18"
              />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          )}
        </span>

        {/* Title */}
        <span
          className={`flex-1 ${isSection ? 'font-semibold' : ''}`}
          onClick={() => onSelectNote(node.note_id)}
        >
          {node.title}
        </span>

        {/* Featured badge */}
        {node.is_featured && (
          <span className="flex-shrink-0 text-yellow-500">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </span>
        )}
      </div>
    </div>
  );
}

interface NotesTreeDraggableProps {
  tree: NoteTreeNode[];
  onSelectNote: (noteId: number) => void;
  selectedNoteId: number | null;
  onReorder: (hierarchyId: number, newOrderIndex: number) => void;
  className?: string;
}

export default function NotesTreeDraggable({
  tree,
  onSelectNote,
  selectedNoteId,
  onReorder,
  className = '',
}: NotesTreeDraggableProps) {
  const [items, setItems] = useState(tree);
  const [expandedNodes, setExpandedNodes] = useState<Set<number>>(new Set());

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setItems((items) => {
        const oldIndex = items.findIndex((item) => item.hierarchy_id === active.id);
        const newIndex = items.findIndex((item) => item.hierarchy_id === over.id);

        const newItems = arrayMove(items, oldIndex, newIndex);

        // Notificar al padre para actualizar en el servidor
        onReorder(active.id as number, newIndex);

        return newItems;
      });
    }
  };

  const toggleExpand = (hierarchyId: number) => {
    setExpandedNodes((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(hierarchyId)) {
        newSet.delete(hierarchyId);
      } else {
        newSet.add(hierarchyId);
      }
      return newSet;
    });
  };

  if (!tree || tree.length === 0) {
    return (
      <div className={`p-4 text-center text-gray-500 dark:text-gray-400 ${className}`}>
        <p>No hay notas en esta colección</p>
        <p className="text-sm mt-2">Añade notas para empezar a organizar tu contenido</p>
      </div>
    );
  }

  return (
    <div className={`overflow-y-auto ${className}`}>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={items.map((i) => i.hierarchy_id)} strategy={verticalListSortingStrategy}>
          {items.map((node) => (
            <div key={node.hierarchy_id}>
              <SortableItem
                node={node}
                level={0}
                onSelectNote={onSelectNote}
                selectedNoteId={selectedNoteId}
                isExpanded={expandedNodes.has(node.hierarchy_id)}
                onToggleExpand={() => toggleExpand(node.hierarchy_id)}
              />
              {/* Children (simplified - no drag for nested) */}
              {expandedNodes.has(node.hierarchy_id) && node.children.length > 0 && (
                <div className="mt-1">
                  {node.children.map((child) => (
                    <div
                      key={child.hierarchy_id}
                      className={`
                        flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer
                        transition-colors duration-150
                        ${selectedNoteId === child.note_id
                          ? 'bg-blue-500 text-white'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                        }
                      `}
                      style={{ paddingLeft: '3rem' }}
                      onClick={() => onSelectNote(child.note_id)}
                    >
                      <span className="flex-shrink-0">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                      </span>
                      <span className="flex-1">{child.title}</span>
                      {child.is_featured && (
                        <span className="flex-shrink-0 text-yellow-500">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </SortableContext>
      </DndContext>
    </div>
  );
}
