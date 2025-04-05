import React from 'react';

const Home = () => {
  return (
    <div className="relative min-h-screen bg-cover bg-center" style={{ backgroundImage: "url('src/assets/pic1.jpg')" }}>
      {/* Overlay */}
      <div className="absolute inset-0 bg-black opacity-50"></div>

      {/* Content */}
      <div className="relative z-10 flex items-center justify-center min-h-screen px-6 md:px-16">
        <div className="max-w-4xl text-center text-white">
          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6 text-white hover:text-amber-400 transition duration-300">
            Welcome to Sevaksha
          </h1>
          <p className="text-lg md:text-xl mb-8 animate-fade-in leading-relaxed tracking-wide">
            Discover your gateway to government welfare schemes. 
            We simplify access to benefits, ensuring transparency and fair distribution for every citizen's prosperity.
            Empowering communities through accessible information and efficient service delivery.
          </p>
          <div className="flex justify-center">
            <button className="bg-amber-500 hover:bg-amber-600 text-white px-6 py-3 rounded-full shadow-lg text-lg transition duration-300">
              Explore Schemes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
