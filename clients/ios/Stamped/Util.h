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
#import "STTypes.h"
#import "STUser.h"
#import "STStamp.h"
#import "STEntity.h"
#import "STUserDetail.h"
#import "STActionContext.h"
#import "STCancellation.h"
#import <QuartzCore/QuartzCore.h>

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

typedef enum STGradientStyle {
    STGradientStyleVertical,
    STGradientStyleHorizontal,
    STGradientStyleStamp,
} STGradientStyle;

@interface Util : NSObject
+ (NSString*)floatToHex:(CGFloat)value;
+ (BOOL)splitHexString:(NSString*)hexString toRed:(CGFloat*)red green:(CGFloat*)green blue:(CGFloat*)blue;
+ (BOOL)splitHexString:(NSString*)hexString toRGB:(CGFloat*)rgb;
+ (UIImage*)whiteMaskedImageUsingImage:(UIImage*)img;
+ (UIImage*)gradientImage:(UIImage*)img
           withPrimaryRed:(CGFloat)pRed
             primaryGreen:(CGFloat)pGreen
              primaryBlue:(CGFloat)pBlue
             secondaryRed:(CGFloat)sRed
           secondaryGreen:(CGFloat)sGreen
            secondaryBlue:(CGFloat)sBlue;
+ (UIImage*)stampImageWithPrimaryColor:(NSString*)primary secondary:(NSString*)secondary;
+ (UIImage*)gradientImage:(UIImage*)image withPrimaryColor:(NSString*)primary secondary:(NSString*)secondary;
+ (UIImage*)gradientImage:(UIImage*)image withPrimaryColor:(NSString*)primary secondary:(NSString*)secondary andStyle:(STGradientStyle)style;

+ (UIImage*)categoryIconForCategory:(NSString*)category subcategory:(NSString*)subcategory filter:(NSString*)filter andSize:(STCategoryIconSize)size;

+ (NSString*)shortUserReadableTimeSinceDate:(NSDate*)date;
+ (NSString*)userReadableTimeSinceDate:(NSDate*)date;

+ (NSString*)sanitizedPhoneNumberFromString:(NSString*)originalNum;
+ (CGRect)frameForImage:(UIImage*)image inImageViewAspectFit:(UIImageView*)imageView;
+ (NSString*)truncateTitleForBackButton:(NSString*)title;

+ (UIView*)imageViewWithURL:(NSURL*)url andFrame:(CGRect)frame;
+ (UIView*)imageViewWithImage:(UIImage*)image andFrame:(CGRect)frame;

+ (UILabel*)viewWithText:(NSString*)text font:(UIFont*)font color:(UIColor*)color mode:(UILineBreakMode)mode andMaxSize:(CGSize)size;
+ (CGSize)sizeWithText:(NSString*)text font:(UIFont*)font mode:(UILineBreakMode)mode andMaxSize:(CGSize)size;

+ (UILabel*)viewWithText:(NSString*)text 
                    font:(UIFont*)font 
                   color:(UIColor*)color
              lineHeight:(CGFloat)lineHeight
                    mode:(UILineBreakMode)mode 
              andMaxSize:(CGSize)size;

+ (CGSize)sizeWithText:(NSString*)text 
                  font:(UIFont*)font 
            lineHeight:(CGFloat)lineHeight 
                  mode:(UILineBreakMode)mode 
            andMaxSize:(CGSize)size;


+ (UIView*)tapViewWithFrame:(CGRect)frame target:(id)target selector:(SEL)selector andMessage:(id)message;
+ (UIView*)tapViewWithFrame:(CGRect)frame andCallback:(STCallback)callback;

+ (CGSize)size:(CGSize)size withScale:(CGFloat)scale;

+ (CGRect)centeredAndBounded:(CGSize)size inFrame:(CGRect)frame;

+ (void)setFullScreenPopUp:(UIView*)view dismissible:(BOOL)dismissible withBackground:(UIColor*)color;

+ (CGFloat)legacyImageScale;

+ (CGFloat)imageScale;

+ (void)logOperationException:(NSException*)exception withMessage:(NSString*)message;

+ (Rdio*)sharedRdio;

+ (CGRect)getAbsoluteFrame:(UIView*)view;

+ (void)runOperationAsynchronously:(NSOperation*)operation;

+ (UINavigationController*)sharedNavigationController;

+ (void)globalLoadingLock;

+ (void)globalLoadingUnlock;

+ (void)globalInteractionLock;

+ (void)globalInteractionUnlock;

+ (void)executeAsync:(void(^)(void))block;

+ (void)executeOnMainThread:(void(^)(void))block;

+ (void)reframeView:(UIView*)view withDeltas:(CGRect)deltas;

+ (CGSize)size:(CGSize)a unionedWith:(CGSize)b;

+ (CGSize)packViews:(NSArray*)views padding:(CGFloat)padding vertical:(BOOL)vertical uniform:(BOOL)uniform;

+ (void)offsetViews:(NSArray*)views byX:(CGFloat)dx andY:(CGFloat)dy;

+ (void)reloadStampedData;

+ (UIImage*)imageForCategory:(NSString*)category;

+ (UIImage*)stampImageForUser:(id<STUser>)user withSize:(STStampImageSize)size;

+ (UIImage*)invertedStampImageForUser:(id<STUser>)user withSize:(STStampImageSize)size;

+ (UIImage*)inboxTodoCategoryImage:(NSString*)category;

+ (UIImage*)highlightedInboxTodoCategoryImage:(NSString*)category;

+ (NSString*)profileImageURLForUser:(id<STUser>)user withSize:(STProfileImageSize)size;

+ (void)confirmWithMessage:(NSString*)message action:(NSString*)action destructive:(BOOL)destructive withBlock:(void(^)(BOOL))block;

+ (void)warnWithMessage:(NSString*)message andBlock:(void(^)(void))block;

+ (void)menuWithTitle:(NSString*)title 
              message:(NSString*)message 
              choices:(NSArray*)strings 
             andBlock:(void(^)(NSString* string))block;

+ (CGRect)relativeFrameForView:(UIView*)view inAncestorView:(UIView*)ancestor;

+ (NSString*)trackLengthString:(NSInteger)length;

+ (CAGradientLayer*)addGradientToLayer:(CALayer*)view withColors:(NSArray*)colors vertical:(BOOL)vertical;

+ (UIView*)profileImageViewForUser:(id<STUser>)user withSize:(NSInteger)size;

/*
+ (UIView*)profileImageViewForUser:(id<STUser>)user 
                              size:(STProfileImageSize)size 
                         andAction:(id<STAction>)action 
                       withContext:(STActionContext*)context;
*/
+ (UIView*)badgeViewForGenre:(NSString*)genre;

+ (CGRect)fullscreenFrame;

+ (CGRect)fullscreenFrameAdjustedForStatusBar;

+ (CGRect)navigatedViewFrame;

+ (CGRect)standardFrameWithNavigationBar:(BOOL)navigationBar;

+ (NSMutableDictionary*)sparseDictionaryForObject:(id)object andKeyPaths:(NSArray*)keyPaths;

+ (NSString*)largeProfileImageURLWithUser:(id<STUser>)user;

+ (NSArray*)categories;

+ (NSString*)entityImageURLForEntityDetail:(id<STEntityDetail>)entityDetail;

+ (NSString*)entityImageURLForEntity:(id<STEntity>)entity;

+ (CGFloat)lineHeightForFont:(UIFont*)font;

+ (void)textInputWithDefault:(NSString*)string andCallback:(void (^)(NSString* value))block;

+ (void)addHomeButtonToController:(UIViewController*)controller withBadge:(BOOL)flag;

+ (STCancellation*)addUnreadBadgeToView:(UIView*)view origin:(CGPoint)origin;

+ (void)addCreateStampButtonToController:(UIViewController*)controller;

+ (void)addConfigurationButtonToController:(UIViewController*)controller;

+ (NSNumber*)numberFromString:(NSString*)string;

+ (void)appendView:(UIView*)child toParentView:(UIView*)parent;

+ (void)removeOldCacheDirectories;

+ (NSURL*)cacheDirectory;

+ (BOOL)isOffline;

+ (void)launchFirstRun;

+ (CGSize)sizeForString:(NSAttributedString*)inString thatFits:(CGSize)inSize;

+ (NSAttributedString *)attributedStringForString:(NSString *)aString 
                                             font:(UIFont *)aFont 
                                            color:(UIColor *)aColor 
                                       lineHeight:(CGFloat)lineHeight 
                                           indent:(CGFloat)indent;

+ (CGFloat)endForString:(NSAttributedString*)string withSize:(CGSize)bounds;

+ (void)drawAttributedString:(NSAttributedString*)string atPoint:(CGPoint)origin withWidth:(CGFloat)width andMaxHeight:(CGFloat)height;

+ (void)setTopRightForView:(UIView*)view toPoint:(CGPoint)point;

+ (void)setBottomLeftForView:(UIView*)view toPoint:(CGPoint)point;

@end
