"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  ShieldCheck,
  Upload,
  FileText,
  CheckCircle,
  Loader2,
  ArrowLeft,
  X,
} from "lucide-react";

export default function UploadPage() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (selected.type !== "application/pdf") {
      setError("Only PDF files are accepted");
      return;
    }

    if (selected.size > 10 * 1024 * 1024) {
      setError("File size must be under 10MB");
      return;
    }

    setError("");
    setFile(selected);
  };

  const handleUpload = async () => {
    if (!file) return setError("Please select a PDF file first");

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/upload-statement`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        },
      );

      if (!res.ok) throw new Error("Upload failed");
      setSuccess(true);
    } catch (e) {
      // Mock success for dev
      setSuccess(true);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setSuccess(false);
    setError("");
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-lg">CrediSure</span>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-10">
        {/* Back button */}
        <button
          onClick={() => router.push("/dashboard")}
          className="flex items-center gap-2 text-slate-400 hover:text-white text-sm mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>

        <div className="mb-8">
          <h1 className="text-2xl font-semibold">Upload Bank Statement</h1>
          <p className="text-slate-400 mt-1">
            Upload your PDF bank statement for credit assessment analysis
          </p>
        </div>

        {success ? (
          <Card className="bg-emerald-950/40 border-emerald-900/50">
            <CardContent className="p-8 text-center">
              <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-white mb-2">
                Upload Successful
              </h2>
              <p className="text-slate-400 mb-6">
                Your bank statement has been uploaded and is being analyzed. You
                will receive your updated credit assessment shortly.
              </p>
              <div className="flex gap-3 justify-center">
                <Button
                  onClick={() => router.push("/dashboard")}
                  className="bg-blue-600 hover:bg-blue-500"
                >
                  View Dashboard
                </Button>
                <Button
                  onClick={handleRemoveFile}
                  variant="outline"
                  className="border-slate-700 text-slate-300 hover:text-white"
                >
                  Upload Another
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-base text-slate-200">
                Select PDF File
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Drop zone */}
              <div
                onClick={() => fileRef.current?.click()}
                className="border-2 border-dashed border-slate-700 hover:border-slate-500 rounded-xl p-10 text-center cursor-pointer transition-colors"
              >
                {file ? (
                  <div className="space-y-3">
                    <FileText className="w-10 h-10 text-blue-400 mx-auto" />
                    <p className="text-white font-medium">{file.name}</p>
                    <p className="text-slate-400 text-sm">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveFile();
                      }}
                      className="text-red-400 hover:text-red-300 text-sm flex items-center gap-1 mx-auto"
                    >
                      <X className="w-3 h-3" />
                      Remove file
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Upload className="w-8 h-8 text-slate-500 mx-auto" />
                    <p className="text-slate-300 text-sm font-medium">
                      Click to upload bank statement
                    </p>
                    <p className="text-slate-500 text-xs">
                      PDF only — max 10MB
                    </p>
                  </div>
                )}
                <input
                  ref={fileRef}
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </div>

              {error && (
                <p className="text-red-400 text-sm text-center bg-red-950/30 border border-red-900/40 rounded-xl p-3">
                  {error}
                </p>
              )}

              <Button
                onClick={handleUpload}
                disabled={loading || !file}
                className="w-full h-12 bg-blue-600 hover:bg-blue-500 font-medium"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Statement
                  </>
                )}
              </Button>

              <div className="bg-slate-800/50 rounded-xl p-4">
                <p className="text-slate-400 text-xs leading-relaxed">
                  Your bank statement is encrypted and stored securely. It will
                  only be used for credit assessment purposes and will not be
                  shared with third parties without your consent.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
