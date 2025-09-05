"use client";
import Image from "next/image";

interface RecommendationsProps {
  selectedCategories: string[];
  loading: boolean;
}

export default function Recommendations({
  selectedCategories,
  loading,
}: RecommendationsProps) {
  return (
    <div className=" w-full h-full flex flex-col gap-12 items-center">
      {/* <h2 className="text-2xl font-bold mb-6 text-center sticky top-0 bg-white z-10 font-playfair">
        Recommendations
      </h2> */}
      {loading && (
        <>
          <h2 className="text-3xl font-bold mb-6 text-center sticky top-0 bg-white z-10 font-playfair">
            Hold on, we are generating recommendations for you...
          </h2>
          <div className="text-center py-8 aspect-square relative w-1/3">
            <Image
              src="/giphy.gif"
              alt="Loading"
              fill
              className="object-cover"
            />
          </div>
        </>
      )}
    </div>
  );
}
