//
//  OAuthToken.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/12/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface OAuthToken : NSObject

@property (nonatomic, copy) NSString* accessToken;
@property (nonatomic, copy) NSString* refreshToken;
@property (nonatomic, assign) CGFloat lifetimeSecs;
@end
