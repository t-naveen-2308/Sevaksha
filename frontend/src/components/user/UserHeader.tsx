import { NavLink } from "react-router-dom";
import Logo from "../../assets/Logo.png";
import { useEffect, useState } from "react";


function UserHeader() {
    const [isScrolled, setIsScrolled] = useState(false);
    const [searchFocused, setSearchFocused] = useState(false);
    const [themeLis, setThemeLis] = useState<[string, string]>(["", ""]);
    console.log(themeLis);
    // Sevaksha color theme
    const navyBlue = "#1e2761";
    const orange = "#f8991d";

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

    useEffect(() => {
        if (localStorage.getItem("theme") === "dark") {
            setThemeLis(["swap-on", "swap-off"]);
        } else {
            setThemeLis(["swap-off", "swap-on"]);
        }
    }, []);

    return (
        <>
            <div
                className={`fixed flex items-center top-0 z-50 w-full transition-all duration-300 ${
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
                    <NavLink
                        to={`/user/home`}
                        className="ml-5 flex items-center"
                    >
                        <img
                            className={`transition-all duration-300 ${isScrolled ? "h-12" : "h-16"} ml-5`}
                            src={Logo}
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
                        className={`w-full max-w-md mx-auto transition-all duration-300 ${
                            searchFocused ? "scale-105" : "scale-100"
                        }`}
                    >
                        <form className="search-form">
                            <div className="flex relative">
                                <input
                                    className="input input-md text-lg border-2 w-full pr-12"
                                    type="search"
                                    placeholder="Search..."
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
                                        border: "none"
                                    }}
                                >
                                    <i className="bi bi-search text-xl"></i>
                                </button>
                            </div>
                        </form>
                    </div>

                    <div className="navbar-nav flex space-x-2">
                        <NavLink
                            className={({ isActive }) =>
                                `nav-item px-4 py-2 text-lg rounded-lg transition-all duration-200 ease-in-out ${
                                    isActive ? "font-bold" : "font-medium"
                                }`
                            }
                            to={`/user/home`}
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
                            to={`/user/my-applications`}
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
                            <i className="bi bi-file-text mr-2"></i>
                            My Applications
                        </NavLink>
                        <NavLink
                            className={({ isActive }) =>
                                `nav-item px-4 py-2 text-lg rounded-lg transition-all duration-200 ease-in-out ${
                                    isActive ? "font-bold" : "font-medium"
                                }`
                            }
                            to="/user/account"
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
                            Account
                        </NavLink>
                    </div>
                </div>
            </div>
            <div style={{ height: "5rem" }}></div>
        </>
    );
}

export default UserHeader;
