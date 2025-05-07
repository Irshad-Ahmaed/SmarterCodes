import { useState } from "react";

interface ResultProps {
  result: string;
  path: string;
  score: number;
  html: string;
}

const ResultCard = ({ result, score, path, html }: ResultProps) => {
  const [showHtml, setShowHtml] = useState(false);

  return (
    <div className="border rounded-lg p-4 shadow bg-white space-y-2">
      {/* Title and Score */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold">{result}</h3>
          <p className="text-sm text-gray-500">Path: {path}</p>
        </div>
        <span className="bg-green-100 text-green-700 text-sm px-2 py-1 rounded">
          {Math.round(score * 100)}% match
        </span>
      </div>

      {/* Toggle HTML */}
      <button
        onClick={() => setShowHtml(!showHtml)}
        className="text-blue-500 text-sm underline cursor-pointer"
      >
        {showHtml ? "Hide HTML" : "View HTML"}
      </button>

      {/* Raw HTML */}
      {showHtml && (
        <pre className="bg-gray-100 text-sm p-2 overflow-x-auto rounded border">
          <code>{html}</code>
        </pre>
      )}
    </div>
  );
};

export default ResultCard;
