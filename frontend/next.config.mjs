/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.rottentomatoes.com',
      },
      {
        protocol: 'https',
        hostname: 'resizing.flixster.com',
      },
    ],
  },
};

export default nextConfig; 
