import React from "react";
import { onAuthStateChanged, signInWithPopup } from "firebase/auth";
import { auth, googleProvider } from "./firebase";
import { useEffect, useState } from "react";
import Wrapper from "./Background";
import { FcGoogle } from "react-icons/fc";
import CategorySelection from "./CategorySelection";

export default function Preferences() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState([]);

  const url = import.meta.env.VITE_USER_MANAGEMENT_API + "/preferences";

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setIsAuthenticated(true);

        try {
          const token = await user.getIdToken();
          const email = user.email;

          const query = new URLSearchParams({ email }).toString();

          const res = await fetch(`${url}?${query}`, {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          });

          if (!res.ok) throw new Error("Failed to fetch");

          const json = await res.json();
          setSelectedCategories(json);

          if (json.preferences?.topic) {
            setSelectedCategories(json.preferences.topic.split(" and "));
          }
        } catch (err) {
          console.error(err);
        }
      } else {
        setIsAuthenticated(false);
      }
    });

    return () => unsubscribe();
  }, []);

  const handleGoogleSignIn = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      console.log("User Info:", result.user);
    } catch (error) {
      console.error("Error during sign in:", error);
    }
  };

  if (!isAuthenticated) {
    return (
      <Wrapper>
        <button className="btn btn-google" onClick={handleGoogleSignIn}>
          Continue with Google
          <FcGoogle className="google-icon" />
        </button>
      </Wrapper>
    );
  }

  return (
    <Wrapper>
      <CategorySelection
        selectedCategories={selectedCategories}
        setSelectedCategories={setSelectedCategories}
      />
    </Wrapper>
  );
}
