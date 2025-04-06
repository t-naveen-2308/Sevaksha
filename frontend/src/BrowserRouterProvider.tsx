import {
    createBrowserRouter,
    RouterProvider,
    Navigate
} from "react-router-dom";
import { Layout, Login, Home, Schemes, Register } from "./components/common";
import {
    AddOrEditUser,
    UserHome,
    MyApplications,
    Account,
    ChangePassword,
    UserLayout
} from "./components/user";
import { RedirectIfNotAuthenticated } from "./utils";
import { useSelector } from "react-redux";

function BrowserRouterProvider() {
    const user = useSelector((state: RootState) => state.user);
    const isAuthenticated = user !== null;

    const BrowserRouter = createBrowserRouter([
        {
            path: "/",
            element: <Layout />,
            children: [
                {
                    path: "home",
                    element: <Home />
                },
                {
                    path: "schemes",
                    element: <Schemes />
                },
                {
                    path: "register",
                    element: <Register />
                },
                {
                    path: "login",
                    element: <Login />
                },
                {
                    path: "",
                    element: <Navigate to="home" />
                }
            ]
        },
        {
            path: "/user",
            element: (
                <RedirectIfNotAuthenticated
                    component={<UserLayout />}
                    isAuthenticated={isAuthenticated}
                />
            ),
            children: [
                {
                    path: "home",
                    element: <UserHome />
                },
                {
                    path: "my-applications",
                    element: <MyApplications />
                },
                {
                    path: "account",
                    element: <Account />
                },
                {
                    path: "edit",
                    element: <AddOrEditUser to="edit" />
                },
                {
                    path: "change-password",
                    element: <ChangePassword />
                },
                {
                    path: "",
                    element: <Navigate to="home" />
                }
            ]
        }
    ]);

    return (
        <>
            <RouterProvider router={BrowserRouter} />
        </>
    );
}

export default BrowserRouterProvider;
