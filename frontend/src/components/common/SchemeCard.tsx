import React from "react";
import {
    Card,
    CardContent,
    CardActions,
    Typography,
    Button,
    Chip,
    Box,
    Divider
} from "@mui/material";
import { Scheme } from "../../types/scheme";
import { NavLink } from "react-router-dom";

interface SchemeCardProps {
    scheme: Scheme;
}

const SchemeCard: React.FC<SchemeCardProps> = ({ scheme }) => {
    return (
        <Card
            sx={{
                width: "100%",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                borderRadius: 3,
                overflow: "hidden",
                border: "1px solid",
                borderColor: "rgba(0,0,0,0.08)",
                transition: "all 0.3s ease-in-out",
                "&:hover": {
                    transform: "translateY(-8px)",
                    boxShadow: "0 12px 24px rgba(0,0,0,0.1)",
                    borderColor: "#f8991d40"
                }
            }}
        >
            <Box
                sx={{
                    bgcolor: "#1e276108",
                    p: 2,
                    borderBottom: "1px solid",
                    borderColor: "rgba(0,0,0,0.05)"
                }}
            >
                <Typography
                    variant="h5"
                    component="h2"
                    fontWeight="bold"
                    color="#1e2761"
                >
                    {scheme.scheme_name}
                </Typography>
            </Box>

            <CardContent
                sx={{
                    flexGrow: 1,
                    p: 3,
                    minHeight: "280px", // Ensures consistent height for card content
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between"
                }}
            >
                <Box>
                    <Box
                        sx={{
                            mb: 2,
                            display: "flex",
                            flexWrap: "wrap",
                            gap: 1
                        }}
                    >
                        {scheme.target_occupation && (
                            <Chip
                                label={scheme.target_occupation}
                                size="small"
                                sx={{
                                    bgcolor: "#1e276110",
                                    color: "#1e2761",
                                    fontWeight: 500
                                }}
                            />
                        )}
                        {scheme.min_age && (
                            <Chip
                                label={`Age ${scheme.min_age} - ${scheme.max_age}`}
                                size="small"
                                sx={{
                                    bgcolor: "#f8991d10",
                                    color: "#f8991d",
                                    fontWeight: 500
                                }}
                            />
                        )}
                    </Box>

                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 2 }}
                    >
                        {scheme.scheme_description}
                    </Typography>
                </Box>

                {scheme.benefits && (
                    <Box>
                        <Divider sx={{ my: 2 }} />
                        <Typography
                            variant="subtitle2"
                            color="#1e2761"
                            fontWeight="bold"
                            gutterBottom
                        >
                            Benefits:
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            {scheme.benefits}
                        </Typography>
                    </Box>
                )}
            </CardContent>

            <CardActions
                sx={{
                    p: 2,
                    pt: 0,
                    gap: 2,
                    height: "72px",
                    display: "flex",
                    justifyContent: "center"
                }}
            >
                {scheme.application_link ? (
                    <>
                        <NavLink to="/login" style={{ flex: 1 }}>
                            <Button
                                variant="contained"
                                fullWidth
                                sx={{
                                    height: "48px",
                                    bgcolor: "#f8991d",
                                    "&:hover": {
                                        bgcolor: "#e88c0d"
                                    },
                                    textTransform: "none",
                                    borderRadius: 2
                                }}
                            >
                                Apply Now
                            </Button>
                        </NavLink>
                        <NavLink to="/login" style={{ flex: 1 }}>
                            <Button
                                variant="outlined"
                                fullWidth
                                sx={{
                                    height: "48px",
                                    color: "#1e2761",
                                    borderColor: "#1e2761",
                                    "&:hover": {
                                        borderColor: "#1e2761",
                                        bgcolor: "#1e276108"
                                    },
                                    textTransform: "none",
                                    borderRadius: 2
                                }}
                            >
                                Learn More
                            </Button>
                        </NavLink>
                    </>
                ) : (
                    <NavLink to="/login" style={{ width: "50%" }}>
                        <Button
                            variant="outlined"
                            fullWidth
                            sx={{
                                height: "48px",
                                color: "#1e2761",
                                borderColor: "#1e2761",
                                "&:hover": {
                                    borderColor: "#1e2761",
                                    bgcolor: "#1e276108"
                                },
                                textTransform: "none",
                                borderRadius: 2
                            }}
                        >
                            Learn More
                        </Button>
                    </NavLink>
                )}
            </CardActions>
        </Card>
    );
};

export default SchemeCard;
