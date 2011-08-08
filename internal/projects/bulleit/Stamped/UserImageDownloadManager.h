//
//  UserImageDownloadManager.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol UserImageDownloaderDelegate
- (void)userImageDidLoad:(UIImage*)image fromURL:(NSString*)imageURL;
@end

extern NSString* const kUserImageLoadedNotification;
extern NSString* const kMediumUserImageLoadedNotification;

@interface UserImageDownloadManager : NSObject <UserImageDownloaderDelegate> {
 @private
  NSMutableDictionary* downloads_;
}

+ (UserImageDownloadManager*)sharedManager;
- (UIImage*)mediumProfileImageAtURL:(NSString*)imageURL;
- (UIImage*)profileImageAtURL:(NSString*)imageURL;

@end
