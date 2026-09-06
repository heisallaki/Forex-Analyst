import { useEffect, useState } from "react";
import {
  Box,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Chip,
  MenuItem,
  Select,
  Switch,
  Typography
} from "@mui/material";
import { AppUser, listUsers, updateUserRole, updateUserStatus } from "@/features/users/api/usersApi";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { useToast } from "@/shared/ui/useToast";
import { useAuthStore } from "@/features/auth/store/authStore";

export function UsersPage() {
  const [users, setUsers] = useState<AppUser[]>([]);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();
  const currentUserId = useAuthStore((state) => state.user?.id);

  const load = () =>
    listUsers()
      .then(setUsers)
      .catch((err) => showToast((err as Error).message, "error"));

  useEffect(() => {
    load()
      .catch(() => undefined)
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRoleChange = async (userId: string, role: string) => {
    try {
      await updateUserRole(userId, role);
      showToast("Role updated. They'll see it after their next login or token refresh.", "success");
      await load();
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleStatusToggle = async (userId: string, isActive: boolean) => {
    try {
      await updateUserStatus(userId, isActive);
      showToast(isActive ? "User reactivated" : "User deactivated", "success");
      await load();
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  if (loading) {
    return <PageLoadingSkeleton variant="table" />;
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 2 }}>
      <PageHeader title="Users" subtitle="Manage roles and account status" />
      <Box sx={{ overflowX: "auto" }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Verified</TableCell>
              <TableCell>Active</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.full_name}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Select
                    size="small"
                    value={user.role}
                    onChange={(e) => handleRoleChange(user.id, e.target.value)}
                  >
                    <MenuItem value="viewer">Viewer</MenuItem>
                    <MenuItem value="analyst">Analyst</MenuItem>
                    <MenuItem value="admin">Admin</MenuItem>
                  </Select>
                </TableCell>
                <TableCell>
                  <Chip size="small" label={user.is_verified ? "✅" : "❌"} variant="outlined" />
                </TableCell>
                <TableCell>
                  <Switch
                    checked={user.is_active}
                    disabled={user.id === currentUserId && user.is_active}
                    onChange={(e) => handleStatusToggle(user.id, e.target.checked)}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Box>
      {users.length === 0 && <Typography color="text.secondary">No users found.</Typography>}
    </Box>
  );
}