"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { 
  Heart, 
  MessageCircle, 
  Share2, 
  Bookmark, 
  MoreHorizontal,
  Camera,
  Video,
  Smile,
  Send,
  Leaf,
  Clock
} from "lucide-react"
import { formatDistanceToNow } from "date-fns"

interface Post {
  id: string
  user: {
    id: string
    username: string
    firstName: string
    lastName: string
    avatarUrl?: string
  }
  title?: string
  content: string
  imageUrl?: string
  videoUrl?: string
  tags?: string[]
  likesCount: number
  commentsCount: number
  sharesCount: number
  isLiked: boolean
  createdAt: string
  postType: string
}

interface Comment {
  id: string
  userId: string
  username: string
  content: string
  createdAt: string
}

export default function SocialFeed() {
  const [posts, setPosts] = useState<Post[]>([])
  const [newPost, setNewPost] = useState({ title: "", content: "", tags: "" })
  const [loading, setLoading] = useState(true)
  const [showComments, setShowComments] = useState<string | null>(null)
  const [comments, setComments] = useState<{ [postId: string]: Comment[] }>({})
  const [newComment, setNewComment] = useState("")

  useEffect(() => {
    loadPosts()
    
    // Set up real-time updates (WebSocket connection would go here)
    // For now, we'll simulate with periodic updates
    const interval = setInterval(loadPosts, 30000) // Refresh every 30 seconds
    
    return () => clearInterval(interval)
  }, [])

  const loadPosts = async () => {
    try {
      // Simulate API call - replace with actual API
      const mockPosts: Post[] = [
        {
          id: "1",
          user: {
            id: "user1",
            username: "plantlover",
            firstName: "Sarah",
            lastName: "Green",
            avatarUrl: "/placeholder.svg?height=40&width=40"
          },
          title: "My Monstera is thriving! 🌱",
          content: "After months of care, my Monstera deliciosa finally has a new leaf! The fenestrations are getting bigger and more beautiful. Here are some tips that worked for me: bright indirect light, weekly watering, and monthly fertilizing. What's your experience with Monsteras?",
          imageUrl: "https://source.unsplash.com/600x400/?monstera+plant",
          tags: ["monstera", "houseplants", "plantcare"],
          likesCount: 24,
          commentsCount: 8,
          sharesCount: 3,
          isLiked: false,
          createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
          postType: "plant-update"
        },
        {
          id: "2",
          user: {
            id: "user2",
            username: "gardenguru",
            firstName: "Mike",
            lastName: "Johnson",
            avatarUrl: "/placeholder.svg?height=40&width=40"
          },
          content: "Quick tip for fellow plant parents: If your plant's leaves are turning yellow, it might be overwatering! Check the soil moisture before watering. Most plants prefer to dry out slightly between waterings. 💧",
          tags: ["plantcare", "tips", "watering"],
          likesCount: 45,
          commentsCount: 12,
          sharesCount: 8,
          isLiked: true,
          createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
          postType: "tip"
        },
        {
          id: "3",
          user: {
            id: "user3",
            username: "succulentqueen",
            firstName: "Emma",
            lastName: "Davis",
            avatarUrl: "/placeholder.svg?height=40&width=40"
          },
          title: "Succulent propagation success! 🌵",
          content: "Started these little babies from leaf cuttings 3 months ago. Now look at them! Propagation is so rewarding and a great way to expand your collection for free. Who else loves propagating?",
          imageUrl: "https://source.unsplash.com/600x400/?succulent+propagation",
          tags: ["succulents", "propagation", "gardening"],
          likesCount: 67,
          commentsCount: 15,
          sharesCount: 12,
          isLiked: false,
          createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
          postType: "showcase"
        }
      ]
      
      setPosts(mockPosts)
    } catch (error) {
      console.error("Error loading posts:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!newPost.content.trim()) return
    
    try {
      // Simulate API call
      const post: Post = {
        id: Date.now().toString(),
        user: {
          id: "current-user",
          username: "you",
          firstName: "Your",
          lastName: "Name",
          avatarUrl: "/placeholder.svg?height=40&width=40"
        },
        title: newPost.title,
        content: newPost.content,
        tags: newPost.tags.split(',').map(tag => tag.trim()).filter(Boolean),
        likesCount: 0,
        commentsCount: 0,
        sharesCount: 0,
        isLiked: false,
        createdAt: new Date().toISOString(),
        postType: "general"
      }
      
      setPosts([post, ...posts])
      setNewPost({ title: "", content: "", tags: "" })
    } catch (error) {
      console.error("Error creating post:", error)
    }
  }

  const handleLike = async (postId: string) => {
    try {
      setPosts(posts.map(post => 
        post.id === postId 
          ? { 
              ...post, 
              isLiked: !post.isLiked,
              likesCount: post.isLiked ? post.likesCount - 1 : post.likesCount + 1
            }
          : post
      ))
    } catch (error) {
      console.error("Error liking post:", error)
    }
  }

  const handleComment = async (postId: string) => {
    if (!newComment.trim()) return
    
    try {
      const comment: Comment = {
        id: Date.now().toString(),
        userId: "current-user",
        username: "you",
        content: newComment,
        createdAt: new Date().toISOString()
      }
      
      setComments(prev => ({
        ...prev,
        [postId]: [...(prev[postId] || []), comment]
      }))
      
      setPosts(posts.map(post => 
        post.id === postId 
          ? { ...post, commentsCount: post.commentsCount + 1 }
          : post
      ))
      
      setNewComment("")
    } catch (error) {
      console.error("Error adding comment:", error)
    }
  }

  const getPostTypeIcon = (type: string) => {
    switch (type) {
      case "plant-update":
        return <Leaf className="h-4 w-4 text-green-500" />
      case "tip":
        return <span className="text-blue-500">💡</span>
      case "showcase":
        return <span className="text-purple-500">🌟</span>
      default:
        return null
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map(i => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="flex items-center space-x-4">
                <div className="rounded-full bg-gray-200 h-10 w-10"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-24"></div>
                  <div className="h-3 bg-gray-200 rounded w-16"></div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Create Post Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Leaf className="h-5 w-5 text-green-500" />
            Share Your Plant Journey
          </CardTitle>
          <CardDescription>
            What's growing in your garden today?
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreatePost} className="space-y-4">
            <Input
              placeholder="Post title (optional)"
              value={newPost.title}
              onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
            />
            <Textarea
              placeholder="Share your thoughts, tips, or plant updates..."
              value={newPost.content}
              onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
              rows={3}
            />
            <Input
              placeholder="Tags (e.g., #succulents, #indoor, #tips)"
              value={newPost.tags}
              onChange={(e) => setNewPost({ ...newPost, tags: e.target.value })}
            />
            <div className="flex justify-between items-center">
              <div className="flex gap-2">
                <Button type="button" variant="outline" size="sm">
                  <Camera className="h-4 w-4 mr-1" />
                  Photo
                </Button>
                <Button type="button" variant="outline" size="sm">
                  <Video className="h-4 w-4 mr-1" />
                  Video
                </Button>
                <Button type="button" variant="outline" size="sm">
                  <Smile className="h-4 w-4 mr-1" />
                  Emoji
                </Button>
              </div>
              <Button type="submit" disabled={!newPost.content.trim()}>
                <Send className="h-4 w-4 mr-1" />
                Share
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Posts Feed */}
      {posts.map((post) => (
        <Card key={post.id} className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <Avatar>
                  <AvatarImage src={post.user.avatarUrl} alt={post.user.username} />
                  <AvatarFallback>
                    {post.user.firstName[0]}{post.user.lastName[0]}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-semibold">
                      {post.user.firstName} {post.user.lastName}
                    </p>
                    <span className="text-sm text-muted-foreground">
                      @{post.user.username}
                    </span>
                    {getPostTypeIcon(post.postType)}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {formatDistanceToNow(new Date(post.createdAt), { addSuffix: true })}
                  </div>
                </div>
              </div>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          
          <CardContent className="pb-3">
            {post.title && (
              <h3 className="text-lg font-semibold mb-2">{post.title}</h3>
            )}
            
            <p className="mb-3 leading-relaxed">{post.content}</p>
            
            {post.imageUrl && (
              <div className="mb-3 rounded-lg overflow-hidden">
                <img
                  src={post.imageUrl}
                  alt="Post image"
                  className="w-full h-64 object-cover hover:scale-105 transition-transform cursor-pointer"
                />
              </div>
            )}
            
            {post.tags && post.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {post.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
          
          <CardFooter className="flex justify-between pt-0">
            <div className="flex gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleLike(post.id)}
                className={`flex items-center gap-1 ${post.isLiked ? 'text-red-500' : ''}`}
              >
                <Heart className={`h-4 w-4 ${post.isLiked ? 'fill-current' : ''}`} />
                <span>{post.likesCount}</span>
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowComments(showComments === post.id ? null : post.id)}
                className="flex items-center gap-1"
              >
                <MessageCircle className="h-4 w-4" />
                <span>{post.commentsCount}</span>
              </Button>
              
              <Button variant="ghost" size="sm" className="flex items-center gap-1">
                <Share2 className="h-4 w-4" />
                <span>{post.sharesCount}</span>
              </Button>
            </div>
            
            <Button variant="ghost" size="sm">
              <Bookmark className="h-4 w-4" />
            </Button>
          </CardFooter>
          
          {/* Comments Section */}
          {showComments === post.id && (
            <div className="border-t px-6 py-4 space-y-4">
              {comments[post.id]?.map((comment) => (
                <div key={comment.id} className="flex gap-3">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="text-xs">
                      {comment.username[0].toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="bg-gray-100 rounded-lg px-3 py-2">
                      <p className="font-semibold text-sm">{comment.username}</p>
                      <p className="text-sm">{comment.content}</p>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDistanceToNow(new Date(comment.createdAt), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              ))}
              
              <div className="flex gap-3">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="text-xs">Y</AvatarFallback>
                </Avatar>
                <div className="flex-1 flex gap-2">
                  <Input
                    placeholder="Write a comment..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleComment(post.id)}
                  />
                  <Button
                    size="sm"
                    onClick={() => handleComment(post.id)}
                    disabled={!newComment.trim()}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}
