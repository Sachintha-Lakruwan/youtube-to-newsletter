import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

let app;
let auth;

export const googleProvider = new GoogleAuthProvider();

export async function initFirebase() {
  if (app) return { app, auth };

  const res = await fetch("/config");
  const firebaseConfig = await res.json();

  app = initializeApp(firebaseConfig);
  auth = getAuth(app);

  return { app, auth };
}
