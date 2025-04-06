import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import {
    Container,
    Grid,
    Typography,
    Box,
    CircularProgress,
    Button
} from "@mui/material";
import SchemeCard from "../common/SchemeCard";
import { createAxios } from "../../utils";
import { Scheme } from "../../types/scheme";

const UserHome = () => {
    const [recommendedSchemes, setRecommendedSchemes] = useState<Scheme[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);

            try {
                const axiosInstance = createAxios(
                    "user",
                    localStorage.getItem("token") ?? undefined
                );
                const response =
                    await axiosInstance.get<Scheme[]>("/recommendation");
                setRecommendedSchemes(response.data || []);
            } catch (error) {
                console.error("Error fetching recommendations:", error);
                setError(
                    "Failed to fetch recommended schemes. Please try again later."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <div
            className="relative min-h-screen bg-cover bg-center"
            style={{ backgroundImage: "url(src/assets/pic1.jpg)" }}
        >
            {/* Overlay */}
            <div className="absolute inset-0 bg-black opacity-50"></div>

            {/* Hero Content */}
            <div className="relative z-10 flex items-center justify-center min-h-[70vh] px-6 md:px-16">
                <div className="max-w-4xl text-center text-white">
                    <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6 text-white hover:text-amber-400 transition duration-300">
                        Welcome to Sevaksha
                    </h1>
                    <p className="text-lg md:text-xl mb-8 animate-fade-in leading-relaxed tracking-wide">
                        Discover your gateway to government welfare schemes. We
                        simplify access to benefits, ensuring transparency and
                        fair distribution for every citizen's prosperity.
                    </p>
                    <div className="flex justify-center">
                        <NavLink
                            to="/schemes"
                            className="bg-amber-500 hover:bg-amber-600 text-white px-6 py-3 rounded-full shadow-lg text-lg transition duration-300"
                        >
                            Explore Schemes
                        </NavLink>
                    </div>
                </div>
            </div>

            {/* Content Below Hero */}
            <div className="relative z-10 bg-white bg-opacity-90 backdrop-blur-sm py-12">
                <Container maxWidth="lg">
                    <Box sx={{ mb: 6 }}>
                        <Typography
                            variant="h3"
                            component="h2"
                            sx={{
                                fontWeight: 700,
                                textAlign: "center",
                                mb: 2,
                                background:
                                    "linear-gradient(45deg, #f8991d, #ffb74d)",
                                WebkitBackgroundClip: "text",
                                WebkitTextFillColor: "transparent"
                            }}
                        >
                            Recommended For You
                        </Typography>
                    </Box>

                    {loading ? (
                        <Box
                            display="flex"
                            justifyContent="center"
                            alignItems="center"
                            minHeight="40vh"
                        >
                            <CircularProgress sx={{ color: "#f8991d" }} />
                        </Box>
                    ) : error ? (
                        <Box
                            sx={{
                                bgcolor: "error.light",
                                p: 3,
                                borderRadius: 2,
                                textAlign: "center"
                            }}
                        >
                            <Typography color="error.main" mb={2}>
                                {error}
                            </Typography>
                            <Button
                                variant="contained"
                                color="error"
                                onClick={() => window.location.reload()}
                            >
                                Retry
                            </Button>
                        </Box>
                    ) : recommendedSchemes.length > 0 ? (
                        <Box
                            sx={{
                                display: "flex",
                                flexWrap: "wrap",
                                gap: 3,
                                justifyContent: "center",
                                alignItems: "stretch"
                            }}
                        >
                            {recommendedSchemes.map((scheme) => (
                                <Box
                                    key={scheme.scheme_id}
                                    sx={{
                                        flexBasis: {
                                            xs: "100%",
                                            sm: "calc(50% - 24px)",
                                            md: "calc(33.333% - 24px)"
                                        },
                                        maxWidth: 345,
                                        display: "flex",
                                        alignItems: "stretch"
                                    }}
                                >
                                    <SchemeCard scheme={scheme} />
                                </Box>
                            ))}
                        </Box>
                    ) : (
                        <Box
                            sx={{
                                textAlign: "center",
                                p: 4,
                                bgcolor: "background.paper",
                                borderRadius: 2,
                                boxShadow: 1
                            }}
                        >
                            <Typography color="text.secondary" mb={2}>
                                No recommended schemes found based on your
                                profile.
                            </Typography>
                            <Button
                                component={NavLink}
                                to="/schemes"
                                variant="contained"
                                sx={{
                                    bgcolor: "#f8991d",
                                    "&:hover": { bgcolor: "#f57c00" }
                                }}
                            >
                                Browse All Schemes
                            </Button>
                        </Box>
                    )}
                </Container>
            </div>
        </div>
    );
};

export default UserHome;
