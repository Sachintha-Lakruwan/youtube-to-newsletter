import "./App.css";
import { signInWithPopup } from "firebase/auth";
import { auth, googleProvider } from "./firebase";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { useEffect, useState } from "react";
import { FcGoogle } from "react-icons/fc";
import Wrapper from "./Background";
import { useNavigate } from "react-router-dom";

function Home() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const handleGoogleSignIn = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      console.log("User Info:", result.user);
    } catch (error) {
      console.error("Error during sign in:", error);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Error during sign out:", error);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

  return (
    <Wrapper>
      <h1 className="hero-title">Youtube to Newsletter</h1>
      <p className="hero-subtitle">
        Get daily digest newsletters summarizing the best content from your
        favorite YouTube channels
      </p>
      <div className="hero-buttons">
        {user ? (
          <div className="user-welcome">
            <p>Welcome, {user.displayName}</p>
            {/* <button className="btn btn-google" onClick={handleSignOut}>
              Sign Out
            </button> */}
            <div className=" flex gap-3">
              <button
                className="btn btn-google "
                onClick={() => navigate("/newsletters")}
              >
                News Letters 📧
              </button>
              <button
                className="btn btn-google "
                onClick={() => navigate("/preferences")}
              >
                Preferences ⚙️
              </button>
            </div>
          </div>
        ) : (
          <button className="btn btn-google" onClick={handleGoogleSignIn}>
            Continue with Google
            <FcGoogle className="google-icon" />
          </button>
        )}
      </div>
    </Wrapper>
  );
}

export default Home;
