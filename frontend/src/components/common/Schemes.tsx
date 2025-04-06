import { useEffect, useState } from "react";
import {
    Container,
    Grid,
    Typography,
    CircularProgress,
    Box
} from "@mui/material";
import createAxios from "../../utils/createAxios";
import SchemeCard from "./SchemeCard";
import { Scheme } from "../../types/scheme";

function Schemes() {
    const [schemes, setSchemes] = useState<Scheme[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        const fetchSchemes = async () => {
            try {
                const axiosInstance = createAxios("main");
                const response = await axiosInstance.get<Scheme[]>("/schemes");
                setSchemes(response.data);
            } catch (error) {
                console.error("Failed to fetch schemes:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchSchemes();
    }, []);
    setSearchTerm('');

    const filteredSchemes = schemes.filter(
        (scheme) =>
            scheme.scheme_name
                .toLowerCase()
                .includes(searchTerm.toLowerCase()) ||
            scheme.scheme_description
                ?.toLowerCase()
                .includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                minHeight="60vh"
            >
                <CircularProgress sx={{ color: "#f8991d" }} />
            </Box>
        );
    }

    return (
        <>
            <Box
                sx={{
                    background:
                        "linear-gradient(135deg, #1e2761 0%, #192346 100%)",
                    color: "white",
                    py: 2, // Reduced from 3 to 2 (16px instead of 24px)
                    mb: 2 // Reduced from 3 to 2 (16px instead of 24px)
                }}
            >
                <Container maxWidth="lg">
                    <Typography
                        variant="h2"
                        component="h1"
                        sx={{
                            fontWeight: 700,
                            textAlign: "center",
                            mb: 1.5, // Reduced from 2 to 1.5 (12px instead of 16px)
                            background:
                                "linear-gradient(45deg, #f8991d, #ffb74d)",
                            WebkitBackgroundClip: "text",
                            WebkitTextFillColor: "transparent"
                        }}
                    >
                        Welfare Schemes
                    </Typography>
                    <Typography
                        variant="h6"
                        textAlign="center"
                        sx={{ mb: 2, color: "#ffffff80" }} // Keep this as is or adjust if needed
                    >
                        Discover government schemes designed to support and
                        empower you
                    </Typography>
                </Container>
            </Box>

            <Container maxWidth="lg">
                {filteredSchemes.length > 0 ? (
                    <Grid container spacing={3} alignItems="stretch">
                        {filteredSchemes.map((scheme) => (
                            <Grid
                                item
                                xs={12}
                                sm={6}
                                md={4}
                                key={scheme.scheme_id}
                                sx={{
                                    display: "flex",
                                    justifyContent: "center"
                                }}
                            >
                                <Box sx={{ width: "100%", maxWidth: 345 }}>
                                    <SchemeCard scheme={scheme} />
                                </Box>
                            </Grid>
                        ))}
                    </Grid>
                ) : (
                    <Typography
                        variant="h6"
                        textAlign="center"
                        sx={{
                            color: "text.secondary",
                            mt: 4
                        }}
                    >
                        No schemes found matching your search.
                    </Typography>
                )}
            </Container>
        </>
    );
};

export default Schemes;
