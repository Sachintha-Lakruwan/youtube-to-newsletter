"use client";
import { useState } from "react";
import CategorySelection from "./components/CategorySelection";
import History from "./components/History";
import Recommendations from "./components/Recommendations";
import ThankYou from "./components/ThankYou";

export default function Home() {
  const [selectedCategories, setSelectedCategories] = useState([""]);
  const [history, setHistory] = useState([""]);
  const [step, setStep] = useState(1);
  const [uniId, setUniId] = useState("");
  function handleNext() {
    if (step == 1) {
      if (selectedCategories.length == 1) {
        alert("Please select at least one category");
        return;
      }
      setStep(2);
    }
    if (step == 2) {
      setStep(3);
    }
    if (step == 3) {
      setStep(4);
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
      {step == 2 && (
        <History
          history={history}
          setHistory={setHistory}
          selectedCategories={selectedCategories}
        />
      )}
      {step == 3 && (
        <Recommendations
          history={history}
          selectedCategories={selectedCategories}
        />
      )}
      {step == 4 && <ThankYou uniId={uniId} setUniId={setUniId} />}
      <button
        onClick={handleNext}
        className=" mb-3 w-[200px] outline-2 outline-green-400 rounded-full py-2 font-semibold transition-all duration-300 hover:bg-green-400 hover:text-white cursor-pointer"
      >
        {step == 4 ? "Submit" : "Next"}
      </button>
      <div className=" w-full h-2 grid grid-cols-4 gap-4 max-w-[200px] mx-auto">
        {Array.from({ length: 4 }).map((_, index) => (
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
