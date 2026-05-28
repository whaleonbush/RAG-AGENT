import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { SUPPORTED_EXTENSIONS } from "../api/types";

interface Props {
  onFiles: (files: File[]) => void;
  disabled?: boolean;
}

const accept = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx", ".xlsm"],
  "text/plain": [".txt", ".md", ".markdown", ".csv"],
};

export default function DropZone({ onFiles, disabled }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted.length) onFiles(accepted);
    },
    [onFiles]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled,
    accept,
    multiple: true,
  });

  const extLabel = SUPPORTED_EXTENSIONS.join(" ");

  return (
    <div
      {...getRootProps()}
      className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${
        isDragActive
          ? "border-blue-500 bg-blue-50"
          : "border-slate-300 bg-white hover:border-blue-400 hover:bg-slate-50"
      } ${disabled ? "pointer-events-none opacity-50" : ""}`}
    >
      <input {...getInputProps()} />
      <p className="text-4xl">📂</p>
      <p className="mt-2 font-medium text-slate-800">
        {isDragActive ? "여기에 놓으세요" : "파일을 끌어다 놓거나 클릭"}
      </p>
      <p className="mt-1 text-sm text-slate-500">여러 파일 동시 업로드 가능</p>
      <p className="mt-2 text-xs text-slate-400">{extLabel}</p>
    </div>
  );
}
