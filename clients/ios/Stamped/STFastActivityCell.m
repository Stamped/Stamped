//
//  STFastActivityCell.m
//  Stamped
//
//  Created by Landon Judkins on 6/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFastActivityCell.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "TTTAttributedLabel.h"
#import "STActionManager.h"
#import "STImageView.h"
#import "STStampedActions.h"
#import "STImageCache.h"
#import "STTextChunk.h"
#import "STChunkGroup.h"
#import "STChunksView.h"
#import "STUserImageView.h"

@interface STFastActivityCellConfiguration : NSObject

- (id)initWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

@property (nonatomic, readonly, retain) id<STActivity> activity;
@property (nonatomic, readonly, assign) STStampedAPIScope scope;

@property (nonatomic, readonly, assign) CGFloat contentOffset;
@property (nonatomic, readonly, assign) CGRect imageFrame;
@property (nonatomic, readonly, assign) CGRect iconFrame;
@property (nonatomic, readonly, assign) BOOL offsetBodyForIcon;
@property (nonatomic, readonly, assign) BOOL hasCredit;
@property (nonatomic, readonly, assign) BOOL iconOnImages;
@property (nonatomic, readonly, assign) CGSize imagesSize;
@property (nonatomic, readonly, assign) BOOL hasImages;
@property (nonatomic, readonly, assign) BOOL hasIcon;
@property (nonatomic, readonly, assign) BOOL useStampIcon;
@property (nonatomic, readonly, assign) BOOL useUserImage;
@property (nonatomic, readonly, assign) BOOL isFollow;
@property (nonatomic, readonly, assign) CGFloat imagesSpacing;

@property (nonatomic, readonly, assign) CGFloat topPadding;
@property (nonatomic, readonly, assign) CGFloat imagePadding;
@property (nonatomic, readonly, assign) CGFloat bottomPadding;
@property (nonatomic, readonly, assign) CGFloat contentYOffset;

@property (nonatomic, readonly, assign) CGFloat contentWidth;

@property (nonatomic, readonly, retain) NSString* header;
@property (nonatomic, readonly, retain) NSString* body;
@property (nonatomic, readonly, retain) NSString* footer;

@property (nonatomic, readonly, retain) STChunk* headerChunk;
@property (nonatomic, readonly, retain) STChunk* bodyChunk;
@property (nonatomic, readonly, retain) STChunk* footerChunk;

@property (nonatomic, readonly, assign) CGFloat headerHeight;
@property (nonatomic, readonly, assign) CGFloat bodyHeight;
@property (nonatomic, readonly, assign) CGFloat imagesHeight;
@property (nonatomic, readonly, assign) CGFloat footerHeight;

@property (nonatomic, readonly, retain) UIFont* headerFontNormal;
@property (nonatomic, readonly, retain) UIFont* headerFontAction;
@property (nonatomic, readonly, retain) UIFont* bodyFontNormal;
@property (nonatomic, readonly, retain) UIFont* bodyFontAction;
@property (nonatomic, readonly, retain) UIFont* footerFontNormal;
@property (nonatomic, readonly, retain) UIFont* footerFontAction;
@property (nonatomic, readonly, retain) UIFont* footerFontTimestamp;

@property (nonatomic, readonly, retain) UIColor* headerColorNormal;
@property (nonatomic, readonly, retain) UIColor* headerColorAction;
@property (nonatomic, readonly, retain) UIColor* bodyColorNormal;
@property (nonatomic, readonly, retain) UIColor* bodyColorAction;
@property (nonatomic, readonly, retain) UIColor* footerColorNormal;
@property (nonatomic, readonly, retain) UIColor* footerColorAction;
@property (nonatomic, readonly, retain) UIColor* footerColorTimestamp;

@property (nonatomic, readonly, assign) CGFloat height;
@property (nonatomic, readonly, retain) NSArray<STUser>* usersForImages;

@end

@implementation STFastActivityCellConfiguration

@synthesize activity = _activity;
@synthesize scope = _scope;

@synthesize headerChunk = _headerChunk;
@synthesize bodyChunk = _bodyChunk;
@synthesize footerChunk = _footerChunk;


- (id)init {
    NSAssert1(NO, @"Shouldn't use init() with %@", self);
    return nil;
}

- (id)initWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
    self = [super init];
    if (self) {
        _activity = [activity retain];
        _scope = scope;
    }
    return self;
}

- (void)dealloc
{
    [_activity release];
    
    [_headerChunk release];
    [_bodyChunk release];
    [_footerChunk release];
    
    [super dealloc];
}

- (CGFloat)contentOffset {
    return 69;
}

- (CGRect)imageFrame {
    if (self.scope == STStampedAPIScopeYou)
        return CGRectMake(10, 8, 44, 44);
    else
        return CGRectMake(24, 8, 28, 28);
}

- (CGRect)iconFrame {
    if (self.scope == STStampedAPIScopeYou) {
        if (self.iconOnImages) {
            return CGRectMake(18, 18, 12, 12);
        }
        else {
            return CGRectMake(42, 40, 17, 17);
        }
    }
    else { 
        return CGRectMake(self.contentOffset, 9.5, 12, 12);
    }
}

- (BOOL)offsetBodyForIcon {
    return self.hasIcon && self.scope != STStampedAPIScopeYou;
}

- (BOOL)hasCredit {
    return self.activity.benefit.integerValue > 0;
}

- (BOOL)isFollow {
    return [self.activity.verb isEqualToString:@"follow"];
}

- (CGFloat)imagesSpacing {
    return self.scope == STStampedAPIScopeYou ? 34 : 55;
}

- (BOOL)iconOnImages {
    if (self.scope == STStampedAPIScopeYou && self.hasIcon && self.hasImages) {
        return YES;
    }
    else {
        return NO;
    }
}

- (BOOL)hasImages {
    return self.usersForImages.count > 0 && (self.scope == STStampedAPIScopeYou || self.isFollow);
}

- (BOOL)useUserImage {
    return self.activity.image == nil;
}

- (BOOL)useStampIcon {
    return self.activity.icon == nil && [self.activity.verb isEqualToString:@"credit"];
}

- (BOOL)hasIcon {
    return self.activity.icon != nil || [self.activity.verb isEqualToString:@"credit"];
}

- (NSString *)header {
    return self.activity.header;
}

- (NSString *)body {
    return self.activity.body;
}

- (NSString *)footer {
    if (self.activity.footer) {
        return self.activity.footer;
    }
    else {
        if (self.hasCredit) {
            NSInteger count = self.activity.benefit.integerValue;
            NSString* format;
            if (count == 1) {
                format = @"You earned %d more stamp!";
            }
            else {
                format = @"You earned %d more stamps!";
            }
            return [NSString stringWithFormat:format, count];
        }
    }
    return nil;
}

- (STChunk*)_chunkWithPrev:(STChunk*)prev
                      text:(NSString*)text
                references:(NSArray<STActivityReference>*)references
                      font:(UIFont*)font 
                     color:(UIColor*)color 
             referenceFont:(UIFont*)referenceFont 
            referenceColor:(UIColor*)referenceColor {
    NSMutableArray* chunks = [NSMutableArray arrayWithObject:prev];
    NSInteger normalIndex = 0;
    if (references) {
        for (id<STActivityReference> reference in references) {
            NSNumber* start = reference.start;
            NSNumber* end = reference.end;
            if (start && end && start.integerValue >= normalIndex && start.integerValue < end.integerValue && end.integerValue <= text.length) {
                NSString* before = [text substringWithRange:NSMakeRange(normalIndex, start.integerValue - normalIndex)];
                if (before.length > 0) {
                    STChunk* normalChunk = [[[STTextChunk alloc] initWithPrev:chunks.lastObject
                                                                         text:before
                                                                         font:font
                                                                        color:color] autorelease];
                    [chunks addObject:normalChunk];
                }
                NSString* active = [text substringWithRange:NSMakeRange(start.integerValue, end.integerValue - start.integerValue)];
                NSAssert1(active.length > 0, @"active length should be non-zero: %@", active);
                STChunk* activeChunk = [[[STTextChunk alloc] initWithPrev:chunks.lastObject
                                                                     text:active
                                                                     font:referenceFont
                                                                    color:referenceColor] autorelease];
                [chunks addObject:activeChunk];
                normalIndex = end.integerValue;
//                if (activeChunk.lineCount > 1) {
//                    NSLog(@"end:%f", activeChunk.end);
//                }
            }
        }
    }
    if (normalIndex < text.length) {
        STChunk* lastChunk = [[[STTextChunk alloc] initWithPrev:chunks.lastObject
                                                           text:[text substringWithRange:NSMakeRange(normalIndex, text.length - normalIndex)]
                                                           font:font
                                                          color:color] autorelease];
        [chunks addObject:lastChunk];
    }
    return [[[STChunkGroup alloc] initWithChunks:chunks] autorelease];
}

- (STChunk*)_contentStartWithYOffset:(CGFloat)y end:(CGFloat)end {
    
    STChunk* start = [[[STChunk alloc] initWithLineHeight:16
                                                    start:0 
                                                      end:end
                                                    width:self.contentWidth
                                                lineCount:1
                                                lineLimit:NSIntegerMax] autorelease];
    y += self.topPadding;
    start.topLeft = CGPointMake(self.contentOffset, y);
    return start;
}

- (STChunk*)headerChunk {
    
    if (!_headerChunk && self.header) {
        STChunk* start = [self _contentStartWithYOffset:0 end:0];
        _headerChunk = [[self _chunkWithPrev:start
                                        text:self.header
                                  references:self.activity.headerReferences
                                        font:self.headerFontNormal
                                       color:self.headerColorNormal
                               referenceFont:self.headerFontAction
                              referenceColor:self.headerColorAction] retain];
    }
    return _headerChunk;
}

- (STChunk*)bodyChunk {
    if (!_bodyChunk && self.body) {
        STChunk* start = [self _contentStartWithYOffset:self.headerHeight end:self.offsetBodyForIcon ? 15 : 0];
        _bodyChunk = [[self _chunkWithPrev:start
                                      text:self.body
                                references:self.activity.bodyReferences
                                      font:self.bodyFontNormal
                                     color:self.bodyColorNormal
                             referenceFont:self.bodyFontAction
                            referenceColor:self.bodyColorAction] retain];
    }
    return _bodyChunk;
}

- (STChunk*)footerChunk {
    if (!_footerChunk) {
        STChunk* start = [self _contentStartWithYOffset:self.headerHeight + self.bodyHeight + self.imagesHeight end:0];
        STChunk* mainChunk = nil;
        NSString* timeString = [Util userReadableTimeSinceDate:self.activity.created];
        if (self.footer) {
            mainChunk = [self _chunkWithPrev:start
                                        text:self.footer
                                  references:self.activity.footerReferences
                                        font:self.footerFontNormal
                                       color:self.footerColorNormal
                               referenceFont:self.footerFontAction
                              referenceColor:self.footerColorAction];
            timeString = [NSString stringWithFormat:@"    %@", timeString];
        }
        
        STChunk* timeChunk = [[[STTextChunk alloc] initWithPrev:mainChunk ? mainChunk : start
                                                           text:timeString
                                                           font:self.footerFontTimestamp
                                                          color:self.footerColorTimestamp] autorelease];
        if (mainChunk) {
            _footerChunk = [[STChunkGroup alloc] initWithChunks:[NSArray arrayWithObjects:mainChunk, timeChunk, nil]];
        }
        else {
            _footerChunk = [timeChunk retain];
        }
    }
    return _footerChunk;
}

- (CGSize)imagesSize {
    if (self.scope == STStampedAPIScopeYou) {
        return CGSizeMake(28, 28);
    }
    else {
        return CGSizeMake(48, 48);
    }
}

- (CGFloat)contentWidth {
    return self.isFollow ? 180 : 216;
}

- (CGFloat)heightWithText:(NSString*)text font:(UIFont*)font andWidth:(CGFloat)width {
    CGFloat value = 0;
    if (text) {
        value = [Util sizeWithText:text
                              font:font
                              mode:UILineBreakModeWordWrap
                        andMaxSize:CGSizeMake(width, CGFLOAT_MAX)].height;
    }
    return value;
}

- (CGFloat)headerHeight {
    if (self.headerChunk) {
        return self.headerChunk.frame.size.height;
    }
    else {
        return 0;
    }
}

- (CGFloat)bodyHeight {
    if (self.bodyChunk) {
        return self.bodyChunk.frame.size.height;
    }
    else {
        return 0;
    }
}

- (CGFloat)imagePadding {
    return 12;
}

- (CGFloat)imagesHeight {
    if (self.hasImages) {
        return self.imagesSize.height + self.imagePadding;
    }
    else {
        return 0;
    }
}

- (CGFloat)footerHeight {
    if (self.footerChunk) {
        return self.footerChunk.frame.size.height;
    }
    else {
        return 0;
    }
}

- (UIFont *)headerFontNormal {
    return [UIFont stampedFontWithSize:10];
}

- (UIFont *)headerFontAction {
    return [UIFont stampedBoldFontWithSize:10];
}

- (UIFont *)bodyFontNormal {
    return [UIFont stampedFontWithSize:12];
}

- (UIFont *)bodyFontAction {
    return [UIFont stampedBoldFontWithSize:12];
}

- (UIFont *)footerFontNormal {
    return [UIFont stampedFontWithSize:10];
}

- (UIFont *)footerFontAction {
    return [UIFont stampedBoldFontWithSize:10];
}

- (UIFont *)footerFontTimestamp {
    return [UIFont stampedFontWithSize:10];
}

- (UIColor *)headerColorNormal {
    return [UIColor colorWithWhite:153/255.0 alpha:1];
}

- (UIColor *)headerColorAction {
    return [UIColor colorWithWhite:153/255.0 alpha:1];
}

- (UIColor *)bodyColorNormal {
    return [UIColor colorWithWhite:89/255.0 alpha:1];
}

- (UIColor *)bodyColorAction {
    return [UIColor colorWithWhite:38/255.0 alpha:1];
}

- (UIColor *)footerColorNormal {
    if (self.hasCredit) {
        return [UIColor colorWithRed:122/255.0 green:158/255.0 blue:203/255.0 alpha:1];
    }
    else {
        return [UIColor colorWithWhite:191/255.0 alpha:1];
    }
}

- (UIColor *)footerColorAction {
    return [self footerColorNormal];
}

- (UIColor *)footerColorTimestamp {
    return [UIColor colorWithWhite:191/255.0 alpha:1];
}

- (CGFloat)topPadding {
    return 4;
}

- (CGFloat)bottomPadding {
    return 12;
}

- (CGFloat)_baseHeight {
    
    CGFloat height = 0;
    height += self.topPadding;
    height += self.headerHeight;
    height += self.bodyHeight;
    height += self.imagesHeight;
    height += self.footerHeight;
    height += self.bottomPadding;
    return height;
}

- (CGFloat)contentYOffset {
    return (self.height - self._baseHeight) / 2;
}

- (CGFloat)height {
    CGFloat min = self.scope == STStampedAPIScopeYou ? 68 : 52;
    return MAX(min, self._baseHeight);
}

- (NSArray<STUser> *)usersForImages {
    if (self.scope == STStampedAPIScopeYou) {
        return self.activity.subjects.count > 1 ? self.activity.subjects : nil;
    }
    else {
        if (self.activity.objects.users.count >= 1) {
            return self.activity.objects.users;
        }
        else {
            return [NSArray array];
        }
    }
}

@end

@interface STFastActivityCell () <TTTAttributedLabelDelegate>

@property (nonatomic, readonly, retain) NSMutableArray* actions;
@property (nonatomic, readonly, retain) id<STActivity> activity;
@property (nonatomic, readonly, retain) STFastActivityCellConfiguration* configuration;
@property (nonatomic, readonly, assign) STStampedAPIScope scope;

@end

@implementation STFastActivityCell

@synthesize actions = actions_;
@synthesize activity = activity_;
@synthesize configuration = _configuration;
@synthesize scope = scope_;

- (void)_addChunk:(STChunk*)chunk {
    if (chunk) {
        UIView* chunkView = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObject:chunk]] autorelease];
        [Util reframeView:chunkView withDeltas:CGRectMake(0, self.configuration.contentYOffset, 0, 0)];
        chunkView.userInteractionEnabled = NO;
        [self.contentView addSubview:chunkView];
    }
}

- (id)initWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"test"];
    if (self) {
        actions_ = [[NSMutableArray alloc] init];
        activity_ = [activity retain];
        scope_ = scope;
        _configuration = [[STFastActivityCellConfiguration alloc] initWithActivity:activity andScope:scope];
        self.accessoryType = UITableViewCellAccessoryNone;
        UIView* imageView = nil;
        if (self.configuration.hasCredit && self.scope == STStampedAPIScopeYou) {
            UIView* background = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, self.configuration.height)] autorelease];
            background.backgroundColor = [UIColor whiteColor];
            [self.contentView addSubview:background];
        }
        if (self.configuration.useUserImage && self.activity.subjects.count > 0) {
            id<STUser> user = [self.activity.subjects objectAtIndex:0];
//            STUserImageView* userImageView = [[[STUserImageView alloc] initWithSize:self.configuration.imageFrame.size.width] autorelease];
//            userImageView.frame = self.configuration.imageFrame;
//            [self addSubview:userImageView];
//            [userImageView setupWithUser:user viewAction:YES];
//            imageView = userImageView;
            imageView = [Util profileImageViewForUser:user withSize:self.configuration.imageFrame.size.width];
            imageView.frame = self.configuration.imageFrame;
            [self.contentView addSubview:imageView];
            [self.contentView addSubview:[Util tapViewWithFrame:imageView.frame target:self selector:@selector(userImageClicked:) andMessage:user]];
        }
        else if (self.activity.image) {
            imageView = [[[UIImageView alloc] initWithFrame:self.configuration.imageFrame] autorelease];
            UIImage* image = [[STImageCache sharedInstance] cachedImageForImageURL:self.activity.image];
            if (image) {
                [(id)imageView setImage:image];
            }
            else {
                [[STImageCache sharedInstance] imageForImageURL:self.activity.image andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                    [(id)imageView setImage:image]; 
                }];
            }
            [self.contentView addSubview:imageView];
        }
        [self _addChunk:self.configuration.headerChunk];
        [self _addChunk:self.configuration.bodyChunk];
        CGFloat y = self.configuration.topPadding;
        y += self.configuration.contentYOffset;
        y += self.configuration.headerHeight;
        y += self.configuration.bodyHeight;
        y += self.configuration.imagePadding;
        if (self.configuration.hasImages) {
            NSArray* users = self.configuration.usersForImages;
            NSInteger max = users.count;
            if (self.scope == STStampedAPIScopeYou) {
                max = MIN(7,max);
            }
            else {
                max = MIN(4,max);
            }
            CGFloat x = self.configuration.contentOffset;
            for (NSInteger i = 0; i < max; i++) {
                id<STUser> currentUser = [users objectAtIndex:i];
                UIView* currentImage = [Util profileImageViewForUser:currentUser withSize:self.configuration.imagesSize.width];
                [Util reframeView:currentImage withDeltas:CGRectMake(x, y, 0, 0)];
                x += self.configuration.imagesSpacing;
                [self addSubview:currentImage];
                if (self.configuration.iconOnImages ) {
                    UIImageView* iconImageView = [[[UIImageView alloc] initWithFrame:self.configuration.iconFrame] autorelease];
                    [Util reframeView:iconImageView withDeltas:CGRectMake(currentImage.frame.origin.x, currentImage.frame.origin.y, 0, 0)];
                    if (self.configuration.useStampIcon) {
                        iconImageView.image = [Util stampImageForUser:currentUser withSize:STStampImageSize12];
                    }
                    else {
                        UIImage* iconImage = [[STImageCache sharedInstance] cachedImageForImageURL:self.activity.icon];
                        if (iconImage) {
                            iconImageView.image = iconImage;
                        }
                        else {
                            [[STImageCache sharedInstance] imageForImageURL:self.activity.icon andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                                iconImageView.image = image; 
                            }];
                        }
                    }
                    [self.contentView addSubview:iconImageView];
                }
                [self.contentView addSubview:[Util tapViewWithFrame:currentImage.frame target:self selector:@selector(userImageClicked:) andMessage:currentUser]];
            }
            if (self.scope != STStampedAPIScopeYou && users.count == 1) {
                id<STUser> userForDetail = [users objectAtIndex:0];
                CGPoint nameOrigin = CGPointMake(self.configuration.contentOffset + 61, y + 20 - self.configuration.bodyFontAction.ascender);
                UIView* nameView = [Util viewWithText:userForDetail.name ? userForDetail.name : @"John Doe"
                                                 font:self.configuration.bodyFontAction
                                                color:self.configuration.bodyColorNormal
                                                 mode:UILineBreakModeTailTruncation
                                           andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
                [Util reframeView:nameView withDeltas:CGRectMake(nameOrigin.x, nameOrigin.y, 0, 0)];
                [self.contentView addSubview:nameView];
                CGPoint screenameOrigin = CGPointMake(self.configuration.contentOffset + 61, y + 36 - self.configuration.headerFontNormal.ascender);
                UIView* screennameView = [Util viewWithText:[NSString stringWithFormat:@"@%@", userForDetail.screenName]
                                                       font:self.configuration.headerFontNormal
                                                      color:self.configuration.headerColorNormal
                                                       mode:UILineBreakModeTailTruncation
                                                 andMaxSize:CGSizeMake(150, CGFLOAT_MAX)];
                [Util reframeView:screennameView withDeltas:CGRectMake(screenameOrigin.x, screenameOrigin.y, 0, 0)];
                [self.contentView addSubview:screennameView];
            }
        }
        [self _addChunk:self.configuration.footerChunk];
        
        if (!self.configuration.iconOnImages && self.configuration.hasIcon) {
            UIImageView* iconView = [[[UIImageView alloc] initWithFrame:self.configuration.iconFrame] autorelease];
            if (self.configuration.useStampIcon) {
                id<STUser> user = [self.activity.subjects objectAtIndex:0];
                UIImage* stampIcon = [Util stampImageForUser:user withSize:STStampImageSize12];
                iconView.image = stampIcon;
            }
            else {
                UIImage* iconImage = [[STImageCache sharedInstance] cachedImageForImageURL:self.activity.icon];
                if (iconImage) {
                    iconView.image = iconImage;
                }
                else {
                    [[STImageCache sharedInstance] imageForImageURL:self.activity.icon andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                        iconView.image = image;
                    }];
                }
            }
            [self.contentView addSubview:iconView];
        }
        if (self.configuration.isFollow && self.scope == STStampedAPIScopeYou) {
            
        }
    }
    return self;
}

- (void)dealloc
{
    [actions_ release];
    [activity_ release];
    [_configuration release];
    [super dealloc];
}

- (void)userImageClicked:(id<STUser>)user {
    NSLog(@"herererere");
    STActionContext* context = [STActionContext context];
    context.user = user;
    id<STAction> action = [STStampedActions actionViewUser:user.userID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)attributedLabel:(TTTAttributedLabel*)label didSelectLinkWithURL:(NSURL*)url {
    NSString* string = [url absoluteString];
    if (![string isEqualToString:@"-1"]) {
        id<STAction> action = [self.actions objectAtIndex:[string integerValue]];
        [[STActionManager sharedActionManager] didChooseAction:action withContext:[STActionContext context]];
    }
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
    [super setSelected:selected animated:animated];
}

+ (CGFloat)heightForCellWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
    STFastActivityCellConfiguration* configuration = [[[STFastActivityCellConfiguration alloc] initWithActivity:activity andScope:scope] autorelease];
    return configuration.height;
}

@end
