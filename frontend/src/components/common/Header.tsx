import { NavLink, useLocation } from "react-router-dom";
import sevakshaLogo from "../../assets/Logo.png";
import { useState, useEffect, FormEvent } from "react";
import createAxios from "../../utils/createAxios";

interface Props {
    setTheme: React.Dispatch<React.SetStateAction<string>>;
}

function Header({setTheme}: Props) {
    const location = useLocation();
    const [isScrolled, setIsScrolled] = useState(false);
    const [searchFocused, setSearchFocused] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [searchResults, setSearchResults] = useState<Scheme[]>(
        []
    );
    const [isLoading, setIsLoading] = useState(false);
    const [showResults, setShowResults] = useState(false);

    // Sevaksha color theme
    const navyBlue = "#1e2761"; // Dark navy for primary elements
    const orange = "#f8991d"; // Orange/gold for accents

    // Handle scroll effect
    useEffect(() => {
        const handleScroll = () => {
            if (window.scrollY > 20) {
                setIsScrolled(true);
            } else {
                setIsScrolled(false);
            }
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const handleSearch = async (e: FormEvent) => {
        e.preventDefault();
        if (!searchTerm.trim()) return;

        setIsLoading(true);
        try {
            const axios = createAxios("main");
            const response = await axios.post<{
                results: Scheme[];
            }>(`/search`, { search_term: searchTerm });
            setSearchResults(response.data.results || []);
            setShowResults(true);
        } catch (error) {
            console.error("Search failed:", error);
        } finally {
            setIsLoading(false);
        }
    };

    // Close results when clicking outside
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (!(e.target as Element).closest(".search-container")) {
                setShowResults(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () =>
            document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <>
            <div
                className={`fixed flex items-center top-0 h-20 z-50 w-full transition-all duration-300 ${
                    isScrolled ? "h-16" : "h-20"
                }`}
                style={{
                    boxShadow: isScrolled
                        ? "rgba(0, 0, 0, 0.1) 0px 4px 12px"
                        : "rgba(0, 0, 0, 0.05) 0px 2px 8px",
                    backgroundColor: "#ffffff"
                }}
            >
                <div className="mx-auto flex justify-between items-center w-11/12">
                    <NavLink to={`/home`} className="ml-5 flex items-center">
                        <img
                            className={`transition-all duration-300 ${isScrolled ? "h-12" : "h-16"} ml-5`}
                            src={sevakshaLogo}
                            alt="Sevaksha Logo"
                        />
                        <span
                            className="ml-3 font-bold text-2xl"
                            style={{ color: navyBlue }}
                        >
                            Sevaksha
                        </span>
                    </NavLink>

                    <div
                        className={`w-full max-w-md mx-auto transition-all duration-300 relative search-container ${
                            searchFocused ? "scale-105" : "scale-100"
                        }`}
                    >
                        <form className="search-form" onSubmit={handleSearch}>
                            <div className="flex relative">
                                <input
                                    value={searchTerm}
                                    onChange={(e) =>
                                        setSearchTerm(e.target.value)
                                    }
                                    name="search_term"
                                    className="input input-md text-lg border-2 w-full pr-12"
                                    type="search"
                                    placeholder="Search welfare schemes..."
                                    aria-label="Search"
                                    maxLength={60}
                                    onFocus={() => setSearchFocused(true)}
                                    onBlur={() => setSearchFocused(false)}
                                    style={{
                                        borderRadius: "2rem",
                                        borderColor: searchFocused
                                            ? orange
                                            : "#d1d5db",
                                        transition: "all 0.3s ease",
                                        outline: "none",
                                        boxShadow: searchFocused
                                            ? `0 0 0 3px ${orange}30`
                                            : "none"
                                    }}
                                />
                                <button
                                    className="absolute right-0 h-full px-4 flex items-center justify-center"
                                    type="submit"
                                    style={{
                                        borderRadius: "0 2rem 2rem 0",
                                        backgroundColor: "transparent",
                                        color: orange,
                                        border: "none",
                                        transition: "all 0.3s ease"
                                    }}
                                >
                                    {isLoading ? (
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-orange-500" />
                                    ) : (
                                        <i className="bi bi-search text-xl"></i>
                                    )}
                                </button>
                            </div>
                        </form>

                        {showResults && searchResults.length > 0 && (
                            <div className="absolute w-full mt-2 bg-white rounded-lg shadow-lg border border-gray-200 max-h-[70vh] overflow-y-auto z-50">
                                {searchResults.map((scheme) => (
                                    <NavLink
                                        key={scheme.scheme_id}
                                        to={`/schemes/${scheme.scheme_id}`}
                                        className="block p-4 hover:bg-gray-50 border-b border-gray-100 last:border-none"
                                        onClick={() => setShowResults(false)}
                                    >
                                        <h3 className="font-semibold text-navy-800 text-lg">
                                            {scheme.scheme_name}
                                        </h3>
                                        {scheme.target_occupation && (
                                            <span className="inline-block px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full mt-1 mb-2">
                                                {scheme.target_occupation}
                                            </span>
                                        )}
                                        {scheme.scheme_description && (
                                            <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                                                {scheme.scheme_description}
                                            </p>
                                        )}
                                        {scheme.benefits && (
                                            <div className="text-xs text-gray-500 flex items-center">
                                                <i className="bi bi-gift mr-1"></i>
                                                <span className="line-clamp-1">
                                                    {scheme.benefits}
                                                </span>
                                            </div>
                                        )}
                                    </NavLink>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="navbar-nav flex space-x-2">
                        <NavLink
                            className={({ isActive }) =>
                                `nav-item px-4 py-2 text-lg rounded-lg transition-all duration-200 ease-in-out ${
                                    isActive ? "font-bold" : "font-medium"
                                }`
                            }
                            to={`/home`}
                            style={({ isActive }) => ({
                                backgroundColor: isActive
                                    ? `${orange}15`
                                    : "transparent",
                                color: isActive ? orange : navyBlue,
                                border: isActive
                                    ? `1px solid ${orange}30`
                                    : "1px solid transparent",
                                transform: isActive
                                    ? "translateY(-2px)"
                                    : "translateY(0)"
                            })}
                        >
                            <i className="bi bi-house mr-2"></i>
                            Home
                        </NavLink>
                        <NavLink
                            className={({ isActive }) =>
                                `nav-item px-4 py-2 text-lg rounded-lg transition-all duration-200 ease-in-out ${
                                    isActive ? "font-bold" : "font-medium"
                                }`
                            }
                            to={`/schemes`}
                            style={({ isActive }) => ({
                                backgroundColor: isActive
                                    ? `${orange}15`
                                    : "transparent",
                                color: navyBlue,
                                border: isActive
                                    ? `1px solid ${orange}30`
                                    : "1px solid transparent",
                                transform: isActive
                                    ? "translateY(-2px)"
                                    : "translateY(0)"
                            })}
                        >
                            <i className="bi bi-award mr-2"></i>
                            Schemes
                        </NavLink>
                        <NavLink
                            className={({ isActive }) =>
                                `nav-item px-4 py-2 text-lg rounded-lg transition-all duration-200 ease-in-out ${
                                    isActive ? "font-bold" : "font-medium"
                                }`
                            }
                            to="/login"
                            style={({ isActive }) => ({
                                backgroundColor: isActive ? navyBlue : orange,
                                color: "#ffffff",
                                transform: isActive
                                    ? "translateY(-2px)"
                                    : "translateY(0)",
                                boxShadow: isActive
                                    ? "0 4px 10px rgba(0,0,0,0.15)"
                                    : "0 2px 5px rgba(0,0,0,0.1)"
                            })}
                        >
                            <i className="bi bi-person mr-2"></i>
                            Login
                        </NavLink>
                    </div>
                </div>
            </div>
            <div style={{ height: "5rem" }}></div>{" "}        </>
    );
}

export default Header;
