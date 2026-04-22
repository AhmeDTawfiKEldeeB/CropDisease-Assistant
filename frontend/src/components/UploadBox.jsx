import { useRef } from "react";

export default function UploadBox({ onFile, preview }) {
  const inputRef = useRef(null);

  const onDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file) onFile(file);
  };

  const onChange = (event) => {
    const file = event.target.files?.[0];
    if (file) onFile(file);
  };

  return (
    <div
      onDragOver={(e) => e.preventDefault()}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
      className="group cursor-pointer rounded-3xl border-2 border-dashed border-primary/40 bg-surface-container-low p-8 transition hover:scale-[1.01] hover:border-primary dark:bg-slate-900"
    >
      <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={onChange} />
      {preview ? (
        <img src={preview} alt="preview" className="h-[440px] w-full rounded-2xl object-cover" />
      ) : (
        <div className="flex h-[440px] flex-col items-center justify-center gap-4 rounded-2xl bg-surface-container-high dark:bg-slate-800">
          <span className="material-symbols-outlined text-5xl text-primary">upload_file</span>
          <p className="text-lg font-semibold">Upload Image</p>
          <p className="text-sm text-on-surface-variant">Drag & drop your image or click to browse</p>
          <p className="text-sm text-on-surface-variant">Supports JPG, PNG, HEIC up to 20MB</p>
        </div>
      )}
    </div>
  );
}