"use client";

import { MovieResult } from "@/types/movie";
import Image from "next/image";
import { useState } from "react";

interface MovieCardProps {
  movie: MovieResult;
}

export default function MovieCard({ movie }: MovieCardProps) {
  const [imageError, setImageError] = useState(false);

  const handleClick = () => {
    if (movie.rt_data?.rt_link) {
      window.open(movie.rt_data.rt_link, "_blank");
    }
  };

  return (
    <div
      onClick={handleClick}
      className="flex gap-4 p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-gray-200"
    >
      {/* Poster */}
      <div className="flex-shrink-0 relative w-32 h-48">
        {movie.rt_data?.poster_url && !imageError ? (
          <Image
            src={movie.rt_data.poster_url}
            alt={`${movie.title} poster`}
            fill
            className="object-cover rounded-md"
            onError={() => setImageError(true)}
            sizes="128px"
          />
        ) : (
          <div className="w-full h-full bg-gray-200 rounded-md flex items-center justify-center">
            <span className="text-gray-400 text-sm text-center px-2">
              No poster available
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex flex-col flex-grow">
        <div className="flex items-start gap-2">
          <h3 className="text-xl font-bold text-gray-900">{movie.title}</h3>
          {movie.rt_data?.release_year && (
            <span className="text-gray-600">
              ({movie.rt_data.release_year})
            </span>
          )}
        </div>

        <p className="mt-2 text-gray-700">{movie.description}</p>

        {movie.rt_data?.cast && (
          <p className="mt-2 text-gray-600">
            <span className="font-medium">Cast:</span> {movie.rt_data.cast}
          </p>
        )}

        {movie.rt_data?.tomato_score && (
          <div className="mt-auto pt-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
              🍅 Critics: {movie.rt_data.tomato_score}/100
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
