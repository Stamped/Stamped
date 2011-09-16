//
//  Util.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@class User;

// Constants from Twitter's developer console.
extern NSString* const kTwitterConsumerKey;
extern NSString* const kTwitterConsumerSecret;
extern NSString* const kTwitterRequestTokenURL;
extern NSString* const kTwitterAuthorizeURL;
extern NSString* const kTwitterAccessTokenURL;

// The OAuth callback URL. This need not be a real URL, but it is used to
// determine authorization success or failure.
extern NSString* const kOAuthCallbackURL;

// A fake URL that GTMOAuth needs as the "scope".
extern NSString* const kTwitterScope;

// The key in the kechain which is used to store auth tokens for Twitter.
extern NSString* const kKeychainTwitterToken;

@interface Util : NSObject
+ (void)splitHexString:(NSString*)hexString toRed:(CGFloat*)red green:(CGFloat*)green blue:(CGFloat*)blue;
+ (UIImage*)whiteMaskedImageUsingImage:(UIImage*)img;
+ (UIImage*)gradientImage:(UIImage*)img
           withPrimaryRed:(CGFloat)pRed
             primaryGreen:(CGFloat)pGreen
              primaryBlue:(CGFloat)pBlue
             secondaryRed:(CGFloat)sRed
           secondaryGreen:(CGFloat)sGreen
            secondaryBlue:(CGFloat)sBlue;
+ (UIImage*)stampImageForUser:(User*)user;
+ (UIImage*)stampImageWithPrimaryColor:(NSString*)primary secondary:(NSString*)secondary;
+ (NSString*)userReadableTimeSinceDate:(NSDate*)date;
@end
