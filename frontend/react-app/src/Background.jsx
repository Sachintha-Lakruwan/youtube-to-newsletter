import "./App.css";

function Wrapper({ children }) {
  return (
    <div className="hero-container">
      <div className="hero-content">{children}</div>
    </div>
  );
}

export default Wrapper;
