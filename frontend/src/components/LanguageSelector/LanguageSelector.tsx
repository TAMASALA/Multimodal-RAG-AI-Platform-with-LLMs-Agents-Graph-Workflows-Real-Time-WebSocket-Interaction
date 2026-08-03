const LANGUAGES = [
  { code: "", label: "No translation" },
  { code: "Spanish", label: "Spanish" },
  { code: "French", label: "French" },
  { code: "German", label: "German" },
  { code: "Hindi", label: "Hindi" },
  { code: "Arabic", label: "Arabic" },
  { code: "Chinese (Simplified)", label: "Chinese (Simplified)" },
  { code: "Japanese", label: "Japanese" },
  { code: "Portuguese", label: "Portuguese" },
];

interface LanguageSelectorProps {
  value: string | null;
  onChange: (language: string | null) => void;
}

export default function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  return (
    <select
      className="language-selector"
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value || null)}
      title="Translate the assistant's answer"
    >
      {LANGUAGES.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.label}
        </option>
      ))}
    </select>
  );
}
