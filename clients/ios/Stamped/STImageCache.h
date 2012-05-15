//
//  STUserImageCache.h
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCancellation.h"
#import "STUser.h"
#import "STEntityDetail.h"
#import "STTypes.h"

@interface STImageCache : NSObject

+ (STImageCache*)sharedInstance;

- (STCancellation*)userImageForUser:(id<STUser>)user 
                               size:(STProfileImageSize)size
                        andCallback:(void(^)(UIImage* image, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entityImageForEntityDetail:(id<STEntityDetail>)entityDetail
                                  andCallback:(void(^)(UIImage* image, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)imageForImageURL:(NSString*)URL
                        andCallback:(void(^)(UIImage* image, NSError* error, STCancellation* cancellation))block;

- (UIImage*)cachedUserImageForUser:(id<STUser>)user 
                              size:(STProfileImageSize)size;

- (UIImage*)cachedEntityImageForEntityDetail:(id<STEntityDetail>)entityDetail;

- (UIImage*)cachedImageForImageURL:(NSString*)URL;

- (void)fastPurge;

@end
