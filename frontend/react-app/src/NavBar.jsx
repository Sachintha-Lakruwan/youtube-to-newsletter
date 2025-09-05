import { useNavigate } from "react-router-dom";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { auth, googleProvider } from "./firebase";
import { signInWithPopup } from "firebase/auth";
import { useEffect, useState } from "react";
import { FcGoogle } from "react-icons/fc";

function NavBar() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      alert("You have signed out successfully!");
    } catch (error) {
      console.error("Error during sign out:", error);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      console.log("User Info:", result.user);
    } catch (error) {
      console.error("Error during sign in:", error);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

  return (
    <div className="absolute top-0 left-0 w-full h-16 z-50 flex items-center justify-between px-12 font-bold">
      <div
        className="cursor-pointer transition-all duration-300 ease-in-out hover:scale-[1.05]"
        onClick={() => navigate("/")}
      >
        Youtube to Newsletter
      </div>

      <div className="flex gap-6">
        <div
          className="cursor-pointer transition-all duration-300 ease-in-out hover:scale-[1.05]"
          onClick={() => navigate("/newsletters")}
        >
          News Letters
        </div>
        <div
          className="cursor-pointer transition-all duration-300 ease-in-out hover:scale-[1.05]"
          onClick={() => navigate("/preferences")}
        >
          Preferences
        </div>
      </div>

      {user ? (
        <div
          className="cursor-pointer transition-all duration-300 ease-in-out hover:scale-[1.05]"
          onClick={handleSignOut}
        >
          Log out
        </div>
      ) : (
        <button
          className="cursor-pointer transition-all duration-300 ease-in-out hover:scale-[1.05] flex items-center gap-3 !bg-transparent !p-0"
          onClick={handleGoogleSignIn}
        >
          Continue with Google
          <FcGoogle className="google-icon" />
        </button>
      )}
    </div>
  );
}

export default NavBar;
