import React, { useEffect, useState } from "react";
import { getAuth } from "firebase/auth";
import { ImSpinner6 } from "react-icons/im";

export default function CategorySelection({
  selectedCategories,
  setSelectedCategories,
}) {
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState("");
  const [loadingSubmit, setLoadingSubmit] = useState(false);
  const [userInfo, setUserInfo] = useState({ email: "", token: "" });
  const url = import.meta.env.VITE_USER_MANAGEMENT_API + "/keywords";
  const url_preferences =
    import.meta.env.VITE_USER_MANAGEMENT_API + "/preferences";
  const auth = getAuth();

  function updateKeyWords() {
    setLoadingSubmit(true);
    const data = {
      email: userInfo.email,
      keywords: selectedCategories,
    };
    console.log(data);
    fetch(url_preferences, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${userInfo.token}`, // send JSON
      },
      body: JSON.stringify(data),
    })
      .then((res) => {
        setLoadingSubmit(false);
        if (!res.ok) throw new Error("Submitting categories was not ok");
        alert("Your preferences updated!");
        return res.json();
      })
      .then((json) => {
        console.log("Response:", json);
      })
      .catch((err) => {
        console.error("Error:", err);
      });
  }

  // function shuffle(array) {
  //   const arr = [...array];
  //   for (let i = arr.length - 1; i > 0; i--) {
  //     const j = Math.floor(Math.random() * (i + 1));
  //     [arr[i], arr[j]] = [arr[j], arr[i]];
  //   }
  //   return arr;
  // }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const user = auth.currentUser;
        if (!user) throw new Error("User not logged in");

        const token = await user.getIdToken();
        setUserInfo({ email: user.email, token: token });

        const res = await fetch(url, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) throw new Error("Failed to fetch");

        const json = await res.json();
        const cats = json.map((obj) => obj.keyword);
        setCategories((cur) => {
          const combined = [...cur, ...cats, ...selectedCategories];
          const unique = [...new Set(combined)];
          unique.sort();
          return unique;
        });
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
  }, [auth.currentUser, url, selectedCategories]);

  return (
    <div className=" w-full h-full flex flex-col gap-12 items-center ">
      <h1 className=" text-3xl font-bold">Pick Some!</h1>
      <div className=" flex flex-wrap justify-center gap-4 max-w-[500px] mx-auto ">
        {categories.map((category) => (
          <div
            className={`px-4 py-1  rounded-full  cursor-pointer transition-all duration-300 hover:shadow-md hover:scale-105 font-semibold ${
              selectedCategories.includes(category)
                ? "bg-green-400 text-white hover:bg-green-300 "
                : "bg-zinc-100 text-zinc-900 hover:bg-zinc-50"
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
      <button
        className=" !rounded-full !w-26 !bg-white !text-zinc-900 cursor-pointer flex items-center justify-center gap-2"
        onClick={updateKeyWords}
      >
        Save{" "}
        <span
          className={`${
            loadingSubmit && "animate-spin inline-block"
          } hidden text-sm`}
        >
          <ImSpinner6 />
        </span>
      </button>
    </div>
  );
}
