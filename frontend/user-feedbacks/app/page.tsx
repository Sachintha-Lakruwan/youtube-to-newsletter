"use client";
import { useState } from "react";
import CategorySelection from "./components/CategorySelection";
// import History from "./components/History";
import Recommendations from "./components/Recommendations";
import ThankYou from "./components/ThankYou";
import History from "./components/History";

interface Video {
  id: string;
  title: string;
  thumbnail: string;
}

interface CategoryResponse {
  user_id: string;
  video_list: Video[];
}

export default function Home() {
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [videos, setVideos] = useState<Video[]>([]);
  const [pickedVideos, setPickedVideos] = useState<string[]>([]);
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [uniId, setUniId] = useState<string>("");
  const [userID, setUserID] = useState<string>("");
  async function handleNext() {
    if (step == 1) {
      if (selectedCategories.length == 0) {
        alert("Please select at least one category");
        return;
      }
      setLoading(true);
      setStep(2);
      try {
        const res = await fetch("/api/ab-testing/categories", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ keywords: selectedCategories }),
        });

        const data: CategoryResponse = await res.json();
        setVideos(data.video_list);
        setUserID(data.user_id);
      } catch (err) {
        console.error("Error fetching videos:", err);
      }
      setLoading(false);
    }
    if (step == 2) {
      if (videos.length == 0) {
        alert("Please select at least one video");
        return;
      }
      setStep(3);
    }
    if (step == 3) {
      try {
        const dataToSubmit = {
          user_id: userID,
          selected_videos: pickedVideos,
          email: uniId,
        };
        const res = await fetch("/api/ab-testing/selected-videos", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(dataToSubmit),
        });

        alert("Your response stored successfully");
        window.location.reload();
      } catch (err) {
        console.error("Error fetching videos:", err);
      }
    }
  }
  return (
    <div className=" w-full h-screen px-48 py-20 flex flex-col items-center">
      {step == 1 && (
        <CategorySelection
          selectedCategories={selectedCategories}
          setSelectedCategories={setSelectedCategories}
        />
      )}
      {step == 2 && loading && (
        <Recommendations
          loading={loading}
          selectedCategories={selectedCategories}
        />
      )}
      {step == 2 && !loading && (
        <History
          history={pickedVideos}
          setHistory={setPickedVideos}
          suggestedVideos={videos}
        />
      )}
      {step == 3 && <ThankYou uniId={uniId} setUniId={setUniId} />}
      <button
        onClick={handleNext}
        className=" mb-3 w-[200px] outline-2 outline-green-400 rounded-full py-2 font-semibold transition-all duration-300 hover:bg-green-400 hover:text-white cursor-pointer"
      >
        {step == 3 ? "Submit" : "Next"}
      </button>
      <div className=" w-full h-2 grid grid-cols-3 gap-4 max-w-[200px] mx-auto">
        {Array.from({ length: 3 }).map((_, index) => (
          <div
            key={index}
            className={`rounded-full ${
              index < step ? "bg-green-400" : "bg-zinc-100"
            }`}
          ></div>
        ))}
      </div>
    </div>
  );
}
