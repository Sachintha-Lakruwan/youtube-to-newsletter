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
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setIsAuthenticated(!!user);
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
