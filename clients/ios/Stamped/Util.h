//
//  Util.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#import "STAction.h"
#import <Rdio/Rdio.h>

@class User;
@class Entity;
@class SearchResult;

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
+ (UIImage*)gradientImage:(UIImage*)image withPrimaryColor:(NSString*)primary secondary:(NSString*)secondary;

+ (NSString*)shortUserReadableTimeSinceDate:(NSDate*)date;
+ (NSString*)userReadableTimeSinceDate:(NSDate*)date;

+ (UIViewController*)detailViewControllerForEntity:(Entity*)entityObject;
+ (UIViewController*)detailViewControllerForSearchResult:(SearchResult*)searchResult;

+ (NSString*)sanitizedPhoneNumberFromString:(NSString*)originalNum;
+ (CGRect)frameForImage:(UIImage*)image inImageViewAspectFit:(UIImageView*)imageView;
+ (NSString*)truncateTitleForBackButton:(NSString*)title;

+ (UIView*)imageViewWithURL:(NSURL*)url andFrame:(CGRect)frame;
+ (UIView*)imageViewWithImage:(UIImage*)image andFrame:(CGRect)frame;
+ (UIView*)viewWithText:(NSString*)text font:(UIFont*)font color:(UIColor*)color mode:(UILineBreakMode)mode andMaxSize:(CGSize)size;
+ (UIView*)tapViewWithFrame:(CGRect)frame target:(id)target selector:(SEL)selector andMessage:(id)message;

+ (CGSize)size:(CGSize)size withScale:(CGFloat)scale;

+ (CGRect)centeredAndBounded:(CGSize)size inFrame:(CGRect)frame;

+ (void)setFullScreenPopUp:(UIView*)view dismissible:(BOOL)dismissible withBackground:(UIColor*)color;

+ (CGFloat)imageScale;

+ (void)logOperationException:(NSException*)exception withMessage:(NSString*)message;

+ (Rdio*)sharedRdio;

@end
