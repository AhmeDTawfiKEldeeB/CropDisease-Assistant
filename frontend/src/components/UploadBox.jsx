import { useRef } from "react";

export default function UploadBox({ onFile, preview, fileName }) {
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
      className="group cursor-pointer rounded-[2rem] border border-[#183f26]/15 bg-white/85 p-4 shadow-[0_24px_60px_rgba(16,56,38,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_28px_70px_rgba(16,56,38,0.12)]"
    >
      <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={onChange} />
      {preview ? (
        <div className="relative overflow-hidden rounded-[1.5rem]">
          <img src={preview} alt="preview" className="h-[480px] w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-black/5 to-transparent" />
          <div className="absolute left-5 top-5 rounded-full bg-black/50 px-3 py-1 text-xs font-semibold text-white backdrop-blur">
            Ready to analyze
          </div>
          <div className="absolute inset-x-0 bottom-0 p-5 text-white">
            <p className="text-xs font-bold uppercase tracking-[0.22em] text-white/75">Uploaded image</p>
            <p className="mt-1 text-lg font-semibold">{fileName || "Selected file"}</p>
          </div>
        </div>
      ) : (
        <div className="flex h-[480px] flex-col items-center justify-center gap-5 rounded-[1.5rem] border-2 border-dashed border-[#235f34]/30 bg-gradient-to-br from-white to-[#eaf3e7] text-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-[#235f34] text-white shadow-sm">
            <span className="material-symbols-outlined text-[34px]">upload_file</span>
          </div>
          <div>
            <p className="text-xl font-bold tracking-tight text-on-surface">Upload Image</p>
            <p className="mt-2 text-sm text-on-surface-variant">Drag & drop your image or click to browse</p>
          </div>
          <div className="flex flex-wrap justify-center gap-2">
            {['JPG', 'PNG', 'HEIC'].map((item) => (
              <span key={item} className="rounded-full bg-[#235f34] px-3 py-1 text-xs font-semibold text-white shadow-sm">
                {item}
              </span>
            ))}
            <span className="rounded-full bg-[#235f34] px-3 py-1 text-xs font-semibold text-white shadow-sm">Up to 20MB</span>
          </div>
        </div>
      )}
    </div>
  );
}