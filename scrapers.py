# -*- coding: utf-8 -*-
"""Collection of API-based scrapers for several social media platforms.

This module demonstrates how to programmatically collect posts from
various social networks using their official APIs. The data is grouped
by ``user_id`` in the returned structure.

Each scraper function yields a dictionary of the form ``{user_id: [posts]}``.
Individual ``post`` structures depend on the platform and are documented
in comments.

Note: This code requires valid API credentials and network connectivity
which are not included here. API clients are used in accordance with the
terms of service of each platform.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Post:
    """Represents a generic social media post."""

    post_id: str
    user_id: str
    content: Any
    metadata: Dict[str, Any]


def collect_from_x(api_client, query: str, max_results: int = 100) -> Dict[str, List[Post]]:
    """Collect posts from X (formerly Twitter) using the official API.

    Parameters
    ----------
    api_client: an authenticated client from `tweepy` or similar.
    query: search query string.
    max_results: maximum number of tweets to fetch.

    Returns
    -------
    dict
        Mapping of user_id to a list of ``Post`` objects.

    Example post format::
        {
            'post_id': '1234567890',
            'user_id': '987654321',
            'content': 'text of the tweet',
            'metadata': {
                'created_at': '2025-01-01T12:00:00Z',
                'lang': 'en',
                'hashtags': ['example'],
            }
        }
    """
    results: Dict[str, List[Post]] = {}

    # Example using tweepy.Client for Twitter API v2
    response = api_client.search_recent_tweets(query=query, max_results=max_results)

    for tweet in response.data or []:
        user_id = tweet.author_id
        post = Post(
            post_id=str(tweet.id),
            user_id=str(user_id),
            content=tweet.text,
            metadata={
                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                'lang': tweet.lang,
                'hashtags': [h['tag'] for h in (tweet.entities.get('hashtags') or [])],
            },
        )
        results.setdefault(str(user_id), []).append(post)

    return results


def collect_from_telegram(client, channel: str, limit: int = 100) -> Dict[str, List[Post]]:
    """Collect messages from a Telegram channel using Telethon.

    Parameters
    ----------
    client: ``telethon.TelegramClient`` logged in with a user account.
    channel: name or ID of the channel to fetch messages from.
    limit: number of messages to retrieve.

    Returns
    -------
    dict mapping user_id to posts. ``user_id`` corresponds to the sender
    of each message.

    Example post format::
        {
            'post_id': '123',
            'user_id': '456',
            'content': 'message text',
            'metadata': {
                'date': '2025-01-01T12:00:00Z',
                'views': 1000,
            }
        }
    """
    from telethon import events  # type: ignore

    results: Dict[str, List[Post]] = {}
    for message in client.iter_messages(entity=channel, limit=limit):
        if message.sender_id is None:
            continue
        post = Post(
            post_id=str(message.id),
            user_id=str(message.sender_id),
            content=message.text,
            metadata={'date': message.date.isoformat(), 'views': message.views},
        )
        results.setdefault(post.user_id, []).append(post)

    return results


def collect_from_youtube(api_client, channel_id: str, max_results: int = 50) -> Dict[str, List[Post]]:
    """Collect videos from a YouTube channel via the Data API.

    Parameters
    ----------
    api_client: an authorized ``googleapiclient.discovery.Resource`` for YouTube.
    channel_id: ID of the YouTube channel.
    max_results: number of videos to fetch.

    Example post format::
        {
            'post_id': 'abcdEFGH',
            'user_id': 'UC123456',
            'content': 'Video Title',
            'metadata': {
                'published_at': '2025-01-01T00:00:00Z',
                'description': 'Video description',
                'view_count': 100,
            }
        }
    """
    results: Dict[str, List[Post]] = {}
    request = api_client.search().list(part='snippet', channelId=channel_id, maxResults=max_results)
    response = request.execute()

    for item in response.get('items', []):
        video_id = item['id'].get('videoId')
        if not video_id:
            continue
        snippet = item['snippet']
        post = Post(
            post_id=video_id,
            user_id=channel_id,
            content=snippet['title'],
            metadata={
                'published_at': snippet['publishedAt'],
                'description': snippet.get('description'),
            },
        )
        results.setdefault(channel_id, []).append(post)

    return results


def collect_from_tiktok(api_client, query: str, limit: int = 50) -> Dict[str, List[Post]]:
    """Collect TikTok posts via the official Research API.

    Parameters
    ----------
    api_client: authenticated client for the TikTok Research API.
    query: hashtag or keyword to search.
    limit: number of videos to fetch.

    Returns a mapping of ``creator_id`` to posts.

    Example post format::
        {
            'post_id': '123',
            'user_id': '987',
            'content': 'Caption text',
            'metadata': {
                'create_time': '2025-01-01T12:00:00Z',
                'like_count': 100,
            }
        }
    """
    results: Dict[str, List[Post]] = {}

    response = api_client.search_videos(query=query, max_count=limit)
    for video in response.get('data', []):
        creator_id = video['author']['id']
        post = Post(
            post_id=video['id'],
            user_id=creator_id,
            content=video.get('desc', ''),
            metadata={
                'create_time': video.get('createTime'),
                'like_count': video.get('stats', {}).get('diggCount'),
            },
        )
        results.setdefault(creator_id, []).append(post)

    return results


def collect_from_xiaohongshu(api_client, keyword: str, limit: int = 50) -> Dict[str, List[Post]]:
    """Collect notes from Xiaohongshu using its official API.

    Parameters
    ----------
    api_client: a session or SDK configured with Xiaohongshu credentials.
    keyword: keyword used to search posts.
    limit: maximum notes to fetch.

    Example post format::
        {
            'post_id': '5f123456',
            'user_id': 'u789',
            'content': 'Title of note',
            'metadata': {
                'likes': 100,
                'comments': 5,
            }
        }
    """
    results: Dict[str, List[Post]] = {}
    params = {
        'keyword': keyword,
        'page_size': limit,
    }
    response = api_client.get('/notes/search', params=params)
    for note in response.get('data', []):
        post = Post(
            post_id=note['id'],
            user_id=note['user_id'],
            content=note.get('title', ''),
            metadata={
                'likes': note.get('likes'),
                'comments': note.get('comments'),
            },
        )
        results.setdefault(post.user_id, []).append(post)

    return results


def collect_from_bilibili(api_client, uid: str, limit: int = 50) -> Dict[str, List[Post]]:
    """Collect videos from Bilibili via its open API.

    Parameters
    ----------
    api_client: a session object or library for calling Bilibili endpoints.
    uid: uploader ID (UID) whose videos will be fetched.
    limit: number of videos to retrieve.

    Example post format::
        {
            'post_id': 'BV1ab411c7',
            'user_id': '12345',
            'content': 'Video title',
            'metadata': {
                'view': 1000,
                'like': 10,
                'danmaku': 50,
            }
        }
    """
    results: Dict[str, List[Post]] = {}

    params = {
        'mid': uid,
        'ps': limit,
        'pn': 1,
    }
    response = api_client.get('https://api.bilibili.com/x/space/arc/search', params=params)
    data = response.get('data', {}).get('list', {}).get('vlist', [])
    for video in data:
        post = Post(
            post_id=video['bvid'],
            user_id=uid,
            content=video['title'],
            metadata={
                'view': video.get('play'),
                'like': video.get('like'),
                'danmaku': video.get('video_review'),
            },
        )
        results.setdefault(uid, []).append(post)

    return results


def merge_results(*sources: Dict[str, List[Post]]) -> Dict[str, List[Post]]:
    """Merge multiple ``{user_id: [posts]}`` mappings into one."""
    merged: Dict[str, List[Post]] = {}
    for source in sources:
        for uid, posts in source.items():
            merged.setdefault(uid, []).extend(posts)
    return merged


__all__ = [
    'Post',
    'collect_from_x',
    'collect_from_telegram',
    'collect_from_youtube',
    'collect_from_tiktok',
    'collect_from_xiaohongshu',
    'collect_from_bilibili',
    'merge_results',
]
