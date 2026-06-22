"use client";

import { useCallback, useRef } from "react";
import { FileText, X } from "lucide-react";

interface Props {
  file: File | null;
  onFile: (f: File | null) => void;
}

export function UploadZone({ file, onFile }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const f = e.dataTransfer.files[0];
      if (f?.type === "application/pdf") onFile(f);
    },
    [onFile],
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0];
      if (f) onFile(f);
    },
    [onFile],
  );

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={() => inputRef.current?.click()}
      className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer transition-all duration-200 hover:border-accent hover:bg-surface-high"
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleChange}
      />
      {file ? (
        <div className="flex items-center justify-center gap-3">
          <FileText size={24} className="text-accent" />
          <span className="text-sm font-medium text-text-primary truncate max-w-[200px]">
            {file.name}
          </span>
          <span className="text-xs text-text-secondary font-mono">
            {(file.size / 1024 / 1024).toFixed(1)} MB
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onFile(null);
            }}
            className="p-1 rounded hover:bg-surface-high text-text-secondary hover:text-rose transition-colors"
          >
            <X size={16} />
          </button>
        </div>
      ) : (
        <>
          <FileText size={36} className="mx-auto text-text-muted mb-3" />
          <p className="text-sm text-text-secondary">
            Drop your research paper here
          </p>
          <p className="text-xs text-text-muted mt-1">PDF up to 50MB</p>
        </>
      )}
    </div>
  );
}
