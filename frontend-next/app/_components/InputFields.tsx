"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Globe, Loader2, Search } from "lucide-react";
import React, { useState } from "react";
import ResultCard from "./ResultCard";

type ResultType = {
  result: string;
  path: string;
  score: number;
  html: string;
};

const InputFields = () => {
  const [urlInput, setUrlInput] = useState<string>("");
  const [queryInput, setQueryInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<ResultType[]>([]);
  const [error, setError] = useState<string | null>(null);

  const searchQuery = async () => {
    if (!urlInput || !queryInput) {
      alert("All fields are required");
      return;
    }
    try {
      setLoading(true);
      setResults([]);
      setError(null);

      const response = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: urlInput,
          query: queryInput,
        }),
      });

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      const data = await response.json();
      console.log(data);
      setResults(data.results || []);
    } catch (error: unknown) {
      console.error(error);

      if (error instanceof Error) {
        setError(error.message || "Something went wrong");
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-10">
      {/* Title */}
      <div className="flex flex-col gap-2 items-center w-full">
        <h2 className="text-3xl font-bold">Website Content Search</h2>
        <p className="text-muted-foreground font-semibold text-sm">
          Search through website content with precision
        </p>
      </div>

      {/* Input */}
      <div className="flex flex-col gap-3">
        <div className="relative">
          <Globe className="size-4 absolute text-muted-foreground left-3 top-3" />
          <Input
            onChange={(e) => setUrlInput(e.target.value)}
            className="pl-10"
            placeholder="Enter Website URL"
          />
        </div>
        <div className="relative">
          <Search className="size-4 absolute text-muted-foreground left-3 top-3" />
          <Input
            onChange={(e) => setQueryInput(e.target.value)}
            className="pl-10"
            placeholder="Enter Your Search Query"
          />
          <Button
            disabled={loading}
            className="absolute right-2 cursor-pointer hover:bg-blue-400 top-1 bg-blue-500"
            onClick={() => searchQuery()}
          >
            {loading ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Searching...
              </>
            ) : (
              "Search"
            )}
          </Button>
        </div>
      </div>

      {/* Search results */}
      <div className="flex flex-col gap-4">
        {error && <div className="text-red-500 text-center">{error}</div>}

        <div className="space-y-4">
          {results.length > 0
            ? results.map((item, idx) => (
                <ResultCard
                  key={idx}
                  result={item.result || "No title"}
                  path={item.path || "/unknown"}
                  score={item.score || 0.8}
                  html={item.html || ""}
                />
              ))
            : !loading &&
              urlInput &&
              queryInput && (
                <p className="text-center text-gray-500">No results found.</p>
              )}
        </div>
      </div>
    </div>
  );
};

export default InputFields;
