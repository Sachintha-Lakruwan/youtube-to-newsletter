"use client";
import React, { useState } from "react";
import { Input } from "@/components/ui/input";

interface CategorySelectionProps {
  selectedCategories: string[];
  setSelectedCategories: (categories: string[]) => void;
}

const youtube_categories = [
  "Vlogs",
  "Education",
  "Technology",
  "Gaming",
  "Entertainment",
  "Music",
  "Beauty & Fashion",
  "Fitness & Health",
  "Food & Cooking",
  "Science & Tech",
  "Finance & Business",
  "Motivational & Self-Help",
  "News & Politics",
  "Travel",
  "Podcasts & Interviews",
  "DIY & Crafts",
  "Automotive",
  "Pets & Animals",
  "Documentary",
  "ASMR & Relaxation",
];

export default function CategorySelection({
  selectedCategories,
  setSelectedCategories,
}: CategorySelectionProps) {
  const [categories, setCategories] = useState(youtube_categories);
  const [newCategory, setNewCategory] = useState("");
  return (
    <div className=" w-full h-full flex flex-col gap-12 items-center">
      <h1 className=" text-3xl font-bold">Pick Some!</h1>
      <div className=" flex flex-wrap justify-center gap-4 max-w-[500px] mx-auto ">
        {categories.map((category) => (
          <div
            className={`px-4 py-1 rounded-full  cursor-pointer transition-all duration-300 hover:shadow-md hover:scale-105 font-semibold ${
              selectedCategories.includes(category)
                ? "bg-green-400 hover:bg-green-300"
                : "bg-zinc-100 hover:bg-zinc-50"
            }`}
            key={category}
            onClick={() => {
              {
                if (selectedCategories.includes(category)) {
                  setSelectedCategories(
                    selectedCategories.filter((c) => c !== category)
                  );
                } else {
                  setSelectedCategories([...selectedCategories, category]);
                }
              }
            }}
          >
            {category}
          </div>
        ))}
      </div>
      <div className=" border-b-1 border-zinc pb-2 max-w-[200px]">
        <input
          type="text"
          placeholder="Add your own.."
          className=" text-center rounded-full font-semibold focus:outline-none focus:ring-0 focus:border-transparent"
          value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              setCategories([...categories, newCategory]);
              setSelectedCategories([...selectedCategories, newCategory]);
              setNewCategory("");
            }
          }}
        />
      </div>
    </div>
  );
}
