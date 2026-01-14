'use client';

import { useState } from 'react';

export interface NoteTreeNode {
  hierarchy_id: number;
  note_id: number;
  title: string;
  note_type: 'section' | 'content';
  is_featured: boolean;
  order_index: number;
  children: NoteTreeNode[];
}

interface TreeNodeProps {
  node: NoteTreeNode;
  level: number;
  onSelectNote: (noteId: number) => void;
  selectedNoteId: number | null;
}

function TreeNode({ node, level, onSelectNote, selectedNoteId }: TreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;
  const isSection = node.note_type === 'section';
  const isSelected = selectedNoteId === node.note_id;

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  const handleSelect = () => {
    onSelectNote(node.note_id);
  };

  return (
    <div className="select-none">
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
        onClick={handleSelect}
      >
        {/* Expand/Collapse Icon */}
        {hasChildren && (
          <button
            onClick={handleToggle}
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

        {/* Icon based on type */}
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
        <span className={`flex-1 ${isSection ? 'font-semibold' : ''}`}>
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

      {/* Children */}
      {hasChildren && isExpanded && (
        <div className="mt-1">
          {node.children.map((child) => (
            <TreeNode
              key={child.hierarchy_id}
              node={child}
              level={level + 1}
              onSelectNote={onSelectNote}
              selectedNoteId={selectedNoteId}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface NotesTreeProps {
  tree: NoteTreeNode[];
  onSelectNote: (noteId: number) => void;
  selectedNoteId: number | null;
  className?: string;
}

export default function NotesTree({
  tree,
  onSelectNote,
  selectedNoteId,
  className = '',
}: NotesTreeProps) {
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
      {tree.map((node) => (
        <TreeNode
          key={node.hierarchy_id}
          node={node}
          level={0}
          onSelectNote={onSelectNote}
          selectedNoteId={selectedNoteId}
        />
      ))}
    </div>
  );
}
