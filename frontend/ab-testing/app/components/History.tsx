"use client";
import React, { useState, useEffect } from "react";
import Image from "next/image";
import { CircleCheck } from "lucide-react";

interface Video {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  publishedAt: string;
  channelTitle: string;
}

interface YouTubeSearchResponse {
  items: Array<{
    id: {
      videoId: string;
    };
    snippet: {
      title: string;
      description: string;
      thumbnails: {
        medium: {
          url: string;
        };
      };
      publishedAt: string;
      channelTitle: string;
    };
  }>;
  error?: {
    message: string;
  };
}

interface CategorySelectionProps {
  history: string[];
  setHistory: (history: string[]) => void;
  selectedCategories: string[];
}

export default function History({
  history,
  setHistory,
  selectedCategories,
}: CategorySelectionProps) {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // YouTube API key - you'll need to replace this with your actual API key
  const YOUTUBE_API_KEY = "";

  useEffect(() => {
    const fetchVideos = async () => {
      if (selectedCategories.length < 2) return;

      // Get all categories except the first one
      const keywords = selectedCategories.slice(1);
      setLoading(true);
      setError(null);

      try {
        // Calculate date range: from last month to day before yesterday
        const today = new Date();
        const dayBeforeYesterday = new Date(today);
        dayBeforeYesterday.setDate(today.getDate() - 2);

        const lastMonth = new Date(today);
        lastMonth.setMonth(today.getMonth() - 1);

        const publishedAfter = lastMonth.toISOString();
        const publishedBefore = dayBeforeYesterday.toISOString();

        // Fetch videos for each keyword
        const allVideos: Video[] = [];

        for (const keyword of keywords) {
          try {
            // Search for most popular English regular videos (excluding shorts) in the selected category within date range
            const response = await fetch(
              `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(
                keyword
              )}&type=video&maxResults=20&order=viewCount&publishedAfter=${publishedAfter}&publishedBefore=${publishedBefore}&videoDuration=medium&relevanceLanguage=en&key=${YOUTUBE_API_KEY}`
            );

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: YouTubeSearchResponse = await response.json();

            if (data.error) {
              throw new Error(data.error.message || "YouTube API error");
            }

            // Filter out shorts and create video list for this keyword
            const keywordVideos: Video[] = data.items
              .filter((item) => {
                const title = item.snippet.title.toLowerCase();
                const description = item.snippet.description.toLowerCase();

                // Exclude videos that are likely shorts
                const isShort =
                  title.includes("#shorts") ||
                  title.includes("short") ||
                  description.includes("#shorts") ||
                  description.includes("short") ||
                  title.includes("tiktok") ||
                  description.includes("tiktok") ||
                  title.includes("reel") ||
                  description.includes("reel");

                return !isShort;
              })
              .slice(0, 4) // Take only first 4 videos per keyword
              .map((item) => ({
                id: item.id.videoId,
                title: item.snippet.title,
                description: item.snippet.description,
                thumbnail: item.snippet.thumbnails.medium.url,
                publishedAt: item.snippet.publishedAt,
                channelTitle: item.snippet.channelTitle,
              }));

            allVideos.push(...keywordVideos);
          } catch (err) {
            console.error(
              `Error fetching videos for keyword "${keyword}":`,
              err
            );
            // Continue with other keywords even if one fails
          }
        }

        // Shuffle the final video list
        const shuffledVideos = allVideos.sort(() => Math.random() - 0.5);

        setVideos(shuffledVideos);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch videos");
        console.error("Error fetching videos:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, [selectedCategories]);

  return (
    <div className="w-full h-full flex flex-col gap-12 items-center overflow-y-scroll mb-8 pb-8">
      <div className="w-full max-w-4xl">
        <h2 className="text-2xl font-bold mb-6 text-center sticky top-0 bg-white z-10 font-playfair">
          Pick what you watched before 🙆‍♂️
        </h2>

        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-2">Loading videos...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong>Error:</strong> {error}
          </div>
        )}

        {!loading && !error && videos.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            {videos.map((video) => (
              <div
                key={video.id}
                className="border aspect-video rounded-lg overflow-hidden "
              >
                <button
                  onClick={() => {
                    if (history.includes(video.id)) {
                      setHistory(history.filter((id) => id !== video.id));
                    } else {
                      setHistory([...history, video.id]);
                    }
                  }}
                  className="w-full h-full bg-red-400 relative cursor-pointer"
                >
                  <Image
                    src={video.thumbnail}
                    alt={video.title}
                    fill
                    className="object-cover transition-all duration-300 hover:scale-105"
                    unoptimized
                    onError={(e) => {
                      // Fallback to background color if image fails to load
                      const target = e.target as HTMLImageElement;
                      target.style.display = "none";
                    }}
                  />
                  {history.includes(video.id) && (
                    <div className=" absolute w-full h-full bg-black/50 top-0 flex justify-center items-center">
                      <p className=" text-4xl scale-200 text-green-400">
                        <CircleCheck />
                      </p>
                    </div>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}

        {!loading &&
          !error &&
          videos.length === 0 &&
          selectedCategories.length >= 2 && (
            <div className="text-center py-8 text-gray-500">
              No videos found for this category.
            </div>
          )}
      </div>
    </div>
  );
}
