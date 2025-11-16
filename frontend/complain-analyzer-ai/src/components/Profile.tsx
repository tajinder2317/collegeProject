import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { useAuth } from '../context/AuthContext';
import { User, Mail, Shield, Building, Edit2, Save, X, Calendar, Activity } from 'lucide-react';

const Profile = () => {
  const { currentUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editedUser, setEditedUser] = useState({
    name: currentUser?.name || '',
    department: currentUser?.department || ''
  });

  const handleEdit = () => {
    setIsEditing(true);
    setEditedUser({
      name: currentUser?.name || '',
      department: currentUser?.department || ''
    });
  };

  const handleSave = () => {
    // TODO: Implement API call to update user profile
    console.log('Saving profile:', editedUser);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedUser({
      name: currentUser?.name || '',
      department: currentUser?.department || ''
    });
  };

  if (!currentUser) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="text-center py-12">
            <User className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500">Please sign in to view your profile</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="grid gap-6 md:grid-cols-3">
        {/* Profile Overview Card */}
        <Card className="md:col-span-1">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4">
              <div className="h-20 w-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                <User className="h-10 w-10 text-white" />
              </div>
            </div>
            <CardTitle className="text-xl">{currentUser.name}</CardTitle>
            <Badge variant={currentUser.role === 'admin' ? 'default' : 'secondary'} className="mt-2">
              {currentUser.role === 'admin' ? (
                <>
                  <Shield className="h-3 w-3 mr-1" />
                  Administrator
                </>
              ) : (
                <>
                  <User className="h-3 w-3 mr-1" />
                  Student
                </>
              )}
            </Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Mail className="h-4 w-4" />
              <span className="truncate">{currentUser.email}</span>
            </div>
            {currentUser.department && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Building className="h-4 w-4" />
                <span>{currentUser.department}</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="h-4 w-4" />
              <span>Member since {new Date().toLocaleDateString()}</span>
            </div>
          </CardContent>
        </Card>

        {/* Profile Details Card */}
        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Profile Information</CardTitle>
            {!isEditing ? (
              <Button variant="outline" size="sm" onClick={handleEdit}>
                <Edit2 className="h-4 w-4 mr-2" />
                Edit Profile
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button size="sm" onClick={handleSave}>
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
                <Button variant="outline" size="sm" onClick={handleCancel}>
                  <X className="h-4 w-4 mr-2" />
                  Cancel
                </Button>
              </div>
            )}
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                <User className="h-5 w-5" />
                Personal Information
              </h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  {isEditing ? (
                    <Input
                      id="name"
                      value={editedUser.name}
                      onChange={(e) => setEditedUser(prev => ({ ...prev, name: e.target.value }))}
                      className="mt-1"
                    />
                  ) : (
                    <p className="mt-1 text-sm text-gray-600">{currentUser.name}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <p className="mt-1 text-sm text-gray-600">{currentUser.email}</p>
                </div>
              </div>
            </div>

            {/* Academic/Professional Information */}
            <div>
              <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                <Building className="h-5 w-5" />
                Academic Information
              </h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label htmlFor="role">Role</Label>
                  <Badge variant={currentUser.role === 'admin' ? 'default' : 'secondary'} className="mt-1">
                    {currentUser.role === 'admin' ? 'Administrator' : 'Student'}
                  </Badge>
                </div>
                <div>
                  <Label htmlFor="department">Department</Label>
                  {isEditing ? (
                    <Input
                      id="department"
                      value={editedUser.department}
                      onChange={(e) => setEditedUser(prev => ({ ...prev, department: e.target.value }))}
                      placeholder="Enter your department"
                      className="mt-1"
                    />
                  ) : (
                    <p className="mt-1 text-sm text-gray-600">
                      {currentUser.department || 'Not specified'}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Account Activity */}
            <div>
              <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Account Activity
              </h3>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">0</div>
                  <div className="text-sm text-gray-600">Complaints Filed</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">0</div>
                  <div className="text-sm text-gray-600">Resolved</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">0</div>
                  <div className="text-sm text-gray-600">Pending</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
