import { useState } from "react";
import "./App.css";

interface RTData {
  rt_link: string;
  poster_url: string;
  tomato_score: string;
  release_year: string | null;
  cast: string | null;
}

interface SearchResult {
  title: string;
  description: string;
  confidence: number;
  rt_data: RTData | null;
}

interface SearchResponse {
  results: SearchResult[];
  query_understood: boolean;
  total_results: number;
}

function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Trim the search query and check if it's empty
    const trimmedQuery = searchQuery.trim();
    if (!trimmedQuery) return;

    setIsLoading(true);
    setResults([]);

    try {
      const response = await fetch(
        `http://127.0.0.1:5000/search?query=${encodeURIComponent(trimmedQuery)}`
      );
      if (!response.ok) {
        throw new Error("Search failed");
      }
      const data: SearchResponse = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error("Search error:", error);
      setError("Failed to fetch results. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="logo">En</div>
      <h1 className="title">Whisper the film that dances in your memory</h1>
      <form onSubmit={handleSearch} className="search-container">
        <input
          type="text"
          placeholder="Search for a movie"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
          disabled={isLoading}
        />
        <button type="submit" className="search-button" disabled={isLoading}>
          <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </form>

      {isLoading && (
        <div className="loading">
          <div className="spinner" />
          <span>Searching for movies...</span>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {!isLoading && results.length > 0 && (
        <div className="results">
          {results.map((result, index) => (
            <div key={index} className="result-item">
              <div className="result-content">
                {result.rt_data?.poster_url && (
                  <div className="poster-container">
                    <img
                      src={result.rt_data.poster_url}
                      alt={`${result.title} poster`}
                      className="movie-poster"
                    />
                  </div>
                )}
                <div className="result-text">
                  <h3>
                    {result.rt_data ? (
                      <a
                        href={result.rt_data.rt_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="movie-title"
                      >
                        {result.title}
                      </a>
                    ) : (
                      result.title
                    )}
                    <div className="score-container">
                      <span className="confidence-score">
                        {Math.round(result.confidence * 100)}% match
                      </span>
                      {result.rt_data?.tomato_score && (
                        <span className="tomato-score">
                          🍅 {result.rt_data.tomato_score}%
                        </span>
                      )}
                    </div>
                  </h3>
                  <p>{result.description}</p>
                  {result.rt_data?.cast && (
                    <div className="cast-info">
                      <span className="cast-label">Cast:</span>{" "}
                      {result.rt_data.cast}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
