"use client";

import { useState } from "react";
import SearchBar from "@/components/SearchBar";
import MovieCard from "@/components/MovieCard";
import { MovieResult, SearchResponse } from "@/types/movie";

export default function Home() {
  const [movies, setMovies] = useState<MovieResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastQuery, setLastQuery] = useState("");

  const searchMovies = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setLastQuery(query);

    try {
      const response = await fetch(
        `http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch results");
      }

      const data: SearchResponse = await response.json();

      if (data.bad_query) {
        setError("Please enter a movie-related search query");
        setMovies([]);
      } else {
        setMovies(data.results);
        if (data.results.length === 0) {
          setError("No movies found");
        }
      }
    } catch (err) {
      setError("Failed to fetch results. Please try again.");
      console.error("Search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMore = async () => {
    if (!lastQuery || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/more", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: lastQuery,
          previous_titles: movies.map((m) => m.title),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch more results");
      }

      const data: SearchResponse = await response.json();

      if (!data.bad_query && data.results.length > 0) {
        setMovies((prev) => [...prev, ...data.results]);
      } else if (data.results.length === 0) {
        setError("No more results available");
      }
    } catch (err) {
      setError("Failed to load more results. Please try again.");
      console.error("Load more error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Cine</h1>
          <SearchBar onSearch={searchMovies} />
        </div>

        {/* Results */}
        <div className="space-y-4">
          {isLoading && movies.length === 0 && (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
            </div>
          )}

          {error && (
            <div className="text-center py-4 text-red-600">{error}</div>
          )}

          {movies.map((movie, index) => (
            <MovieCard key={`${movie.title}-${index}`} movie={movie} />
          ))}

          {movies.length > 0 && (
            <div className="text-center py-4">
              <button
                onClick={loadMore}
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? "Loading..." : "Generate More"}
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
