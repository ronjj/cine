export interface RTData {
  rt_link: string;
  poster_url: string;
  tomato_score: string;
  release_year?: string;
  cast?: string;
}

export interface MovieResult {
  title: string;
  description: string;
  confidence: number;
  rt_data?: RTData;
}

export interface SearchResponse {
  results: MovieResult[];
  query_understood: boolean;
  total_results: number;
  bad_query: boolean;
} 
