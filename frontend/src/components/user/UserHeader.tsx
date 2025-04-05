import { NavLink, useLocation } from "react-router-dom";
import libraryLogo from "../../assets/libraryLogo.png";
import libraryLogoDark from "../../assets/libraryLogoDark.png";
import { useEffect, useState } from "react";

interface Props {
    setTheme: React.Dispatch<React.SetStateAction<string>>;
}

function UserHeader({ setTheme }: Props) {
    const location = useLocation();
    const [themeLis, setThemeLis] = useState<[string, string]>(["", ""]);

    useEffect(() => {
        if (localStorage.getItem("theme") === "dark") {
            setThemeLis(["swap-on", "swap-off"]);
        } else {
            setThemeLis(["swap-off", "swap-on"]);
        }
    }, []);

    return (
        <>
            <p>&nbsp;</p>
            <div
                className={
                    "fixed flex items-center top-0 h-20 z-50 w-full " +
                    (localStorage.getItem("theme") &&
                    localStorage.getItem("theme") === "light"
                        ? "bg-base-100"
                        : "bg-base-200")
                }
                style={{ boxShadow: "rgba(0, 0, 0, 0.24) 0px 3px 8px" }}
            >
                <div className="mx-auto flex justify-between items-center w-11/12">
                    <NavLink
                        to={`/user/home`}
                        className="ml-5"
                    >
                        <img
                            className="h-12 ml-1"
                            src={
                                localStorage.getItem("theme") &&
                                localStorage.getItem("theme") === "light"
                                    ? libraryLogo
                                    : libraryLogoDark
                            }
                            alt="Library Logo"
                        />
                    </NavLink>
                    <div className="w-full max-w-md mx-auto">
                        <form className="search-form" action="" method="POST">
                            <div className="flex">
                                <input
                                    name="search_term"
                                    className="input input-md text-lg input-bordered border-2 border-r-0 w-full"
                                    type="search"
                                    placeholder="Search..."
                                    aria-label="Search"
                                    maxLength={60}
                                    style={{
                                        borderRadius: "0.5rem 0rem 0rem 0.5rem"
                                    }}
                                />
                                <button
                                    className="btn btn-blue"
                                    type="submit"
                                    style={{
                                        borderRadius: "0rem 0.5rem 0.5rem 0rem"
                                    }}
                                >
                                    <i className="bi bi-search text-lg"></i>
                                </button>
                            </div>
                        </form>
                    </div>
                    <div className="navbar-nav flex space-x-1">
                        <NavLink
                            className={
                                "nav-item btn btn-ghost px-3 text-lg "
                            }
                            to={`/user/home`}
                        >
                            Home
                        </NavLink>
                        <NavLink
                            className={
                                "nav-item btn btn-ghost px-3 text-lg "
                            }
                            to={`/user/my-applications`}
                        >
                            My Applications
                        </NavLink>
                            <NavLink
                                className={
                                    "nav-item btn btn-ghost px-3 text-lg "
                                }
                                to="/user/account"
                            >
                                Account
                            </NavLink>
                    </div>
                </div>
            </div>
        </>
    );
}

export default UserHeader;
