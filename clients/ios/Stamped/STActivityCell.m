//
//  STActivityCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActivityCell.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "TTTAttributedLabel.h"
#import "STActionManager.h"
#import "STImageView.h"
#import "STStampedActions.h"
#import "STImageCache.h"

@interface STActivityCellConfiguration : NSObject

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
@property (nonatomic, readonly, assign) CGFloat imagesSpacing;

@property (nonatomic, readonly, assign) CGFloat headerPadding;
@property (nonatomic, readonly, assign) CGFloat bodyPadding;
@property (nonatomic, readonly, assign) CGFloat imagesPadding;
@property (nonatomic, readonly, assign) CGFloat footerPadding;
@property (nonatomic, readonly, assign) CGFloat bottomPadding;

@property (nonatomic, readonly, assign) CGFloat headerWidth;
@property (nonatomic, readonly, assign) CGFloat bodyWidth;
@property (nonatomic, readonly, assign) CGFloat footerWidth;

@property (nonatomic, readonly, retain) NSString* header;
@property (nonatomic, readonly, retain) NSString* body;
@property (nonatomic, readonly, retain) NSString* footer;
@property (nonatomic, readonly, assign) NSInteger bodyReferenceOffset;

@property (nonatomic, readonly, copy) NSNumber* headerHeight;
@property (nonatomic, readonly, copy) NSNumber* bodyHeight;
@property (nonatomic, readonly, copy) NSNumber* imagesHeight;
@property (nonatomic, readonly, copy) NSNumber* footerHeight;

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

@implementation STActivityCellConfiguration

@synthesize activity = _activity;
@synthesize scope = _scope;

@synthesize headerHeight = _headerHeight;
@synthesize bodyHeight = _bodyHeight;
@synthesize imagesHeight = _imagesHeight;
@synthesize footerHeight = _footerHeight;


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
    
    [_headerHeight release];
    [_bodyHeight release];
    [_imagesHeight release];
    [_footerHeight release];
    
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
    return self.hasIcon && self.scope == STStampedAPIScopeFriends;
}

- (BOOL)hasCredit {
    return self.activity.benefit.integerValue > 0;
}

- (CGFloat)imagesSpacing {
    return self.scope == STStampedAPIScopeYou ? 34 : 55;
}

- (BOOL)iconOnImages {
    if (self.scope == STStampedAPIScopeYou) {
        return YES;
    }
    else {
        return NO;
    }
}

- (BOOL)hasImages {
    return self.usersForImages.count > 0;
}

- (BOOL)useUserImage {
    return self.activity.image == nil;
}

- (BOOL)useStampIcon {
    return self.activity.icon == nil && self.activity.subjects.count > 0;
}

- (BOOL)hasIcon {
    return self.activity.icon != nil || [self.activity.verb isEqualToString:@"credit"];
}

- (NSString *)header {
    return self.activity.header;
}

- (NSString *)body {
    if (!self.activity.body) return nil;
    NSString* filler = [@"" stringByPaddingToLength:self.bodyReferenceOffset withString:@" " startingAtIndex:0];
    return [NSString stringWithFormat:@"%@%@", filler, self.activity.body];
}

- (NSString *)footer {
    if (self.activity.footer) {
        return self.activity.footer;
    }
    else {
        if (self.hasCredit) {
            NSInteger count = self.activity.benefit.integerValue;
            NSString* format;
            if (count > 1) {
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

- (NSInteger)bodyReferenceOffset {
    if (self.offsetBodyForIcon) {
        return 5;
    }
    else {
        return 0;
    }
}

- (CGSize)imagesSize {
    if (self.scope == STStampedAPIScopeYou) {
        return CGSizeMake(28, 28);
    }
    else {
        return CGSizeMake(48, 48);
    }
}

- (CGFloat)headerWidth {
    return 216;
}

- (CGFloat)bodyWidth {
    return self.headerWidth;
}

- (CGFloat)footerWidth {
    return self.headerWidth;
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

- (NSNumber *)headerHeight {
    if (!_headerHeight) {
        _headerHeight = [[NSNumber numberWithFloat:[self heightWithText:self.header font:self.headerFontNormal andWidth:self.headerWidth]] retain];
    }
    return _headerHeight;
}

- (NSNumber *)bodyHeight {
    if (!_bodyHeight) {
        _bodyHeight = [[NSNumber numberWithFloat:[self heightWithText:self.body font:self.bodyFontNormal andWidth:self.bodyWidth]] retain];
    }
    return _bodyHeight;
}

- (NSNumber *)imagesHeight {
    if (!_imagesHeight) {
        CGFloat value = 0;
        if (self.hasImages) {
            value = self.imagesSize.height;
        }
        _imagesHeight = [[NSNumber numberWithFloat:value] retain];
    }
    return _imagesHeight;
}

- (NSNumber *)footerHeight {
    if (!_footerHeight) {
        _footerHeight = [[NSNumber numberWithFloat:[self heightWithText:self.footer font:self.footerFontNormal andWidth:self.footerWidth]] retain];
        if (_footerHeight.floatValue < 1) { 
            [_footerHeight release];
            _footerHeight = [[NSNumber numberWithFloat:[self heightWithText:@"time" font:self.footerFontTimestamp andWidth:self.footerWidth]] retain];
        }
    }
    return _footerHeight;
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

- (CGFloat)headerPadding {
    if (self.header) {
        return 20 -  self.headerFontNormal.ascender - 1;
    }
    else {
        return 0;
    }
}

- (CGFloat)bodyPadding {
    if (self.header) {
        return 16 - self.headerFontNormal.descender - self.bodyFontNormal.ascender - 6; //compensated
    }
    else {
        if (self.scope == STStampedAPIScopeYou) {
            if (self.bodyHeight.integerValue > 16 || self.hasImages) {
                return 24 - self.bodyFontNormal.ascender - 1;
            }
            else {
                return 28 - self.bodyFontNormal.ascender - 1;
            }
        }
        else {
            return 20 - self.bodyFontNormal.ascender - 1;
        }
    }
}

- (CGFloat)imagesPadding {
    if (self.hasImages) {
        return 12 - self.bodyFontNormal.descender;
    }
    else {
        return 0;
    }
}

- (CGFloat)footerPadding {
    if (self.hasImages) {
        return 16 - self.footerFontNormal.ascender;
    }
    else {
        return 16 - self.bodyFontNormal.descender - self.footerFontNormal.ascender - 6; //compensated
    }
}

- (CGFloat)bottomPadding {
    return 12 - self.footerFontNormal.descender - 1;
}

- (CGFloat)height {
    CGFloat height = 0;
    height += self.headerPadding;
    height += self.headerHeight.floatValue;
    height += self.bodyPadding;
    height += self.bodyHeight.floatValue;
    height += self.imagesPadding;
    height += self.imagesHeight.floatValue;
    height += self.footerPadding;
    height += self.footerHeight.floatValue;
    height += self.bottomPadding;
    return height;
}

- (NSArray<STUser> *)usersForImages {
    if (self.scope == STStampedAPIScopeYou) {
        return self.activity.subjects.count > 1 ? self.activity.subjects : nil;
    }
    else {
        if (self.activity.objects.users.count > 1) {
            return self.activity.objects.users;
        }
        else if (self.activity.subjects.count > 1) {
            return self.activity.subjects;
        }
        else {
            return self.activity.objects.users;
        }
    }
}

@end

@interface STActivityCell () <TTTAttributedLabelDelegate>

@property (nonatomic, readonly, retain) NSMutableArray* actions;
@property (nonatomic, readonly, retain) id<STActivity> activity;
@property (nonatomic, readonly, retain) STActivityCellConfiguration* configuration;
@property (nonatomic, readonly, assign) STStampedAPIScope scope;

@end

@implementation STActivityCell

@synthesize actions = actions_;
@synthesize activity = activity_;
@synthesize configuration = _configuration;
@synthesize scope = scope_;

/*
 - (void)addUserImagesForUsers:(NSArray<STUser>*)users inView:(UIView*)view {
 NSInteger imageLimit = MIN(4, self.activity.subjects.count);
 CGRect imagesBounds = [STActivityCell imagesBoundsForActivity:self.activity andScope:self.scope];
 for (NSInteger i = 0; i < imageLimit; i++) {
 CGFloat size = 28;
 CGFloat padding = 5;
 id<STUser> subjectUser = [self.activity.subjects objectAtIndex:i];
 UIView* imageView = [Util profileImageViewForUser:subjectUser withSize:size];
 [Util reframeView:imageView withDeltas:CGRectMake(imagesBounds.origin.x + (size + padding) * i, imagesBounds.origin.y, 0, 0)];
 [view addSubview:imageView];
 UIView* imageButton = [Util tapViewWithFrame:imageView.frame target:self selector:@selector(userImageClicked:) andMessage:subjectUser];
 [view addSubview:imageButton];
 }
 }
 */

- (CGFloat)addAttributedText:(NSString*)text 
                       frame:(CGRect)frame 
                        font:(UIFont*)font 
                       color:(UIColor*)color 
                      offset:(NSInteger)offset
                  references:(NSArray<STActivityReference>*)references 
                      toView:(UIView*)view {
    TTTAttributedLabel* bodyView = [[[TTTAttributedLabel alloc] initWithFrame:frame] autorelease];
    bodyView.backgroundColor = [UIColor clearColor];
    bodyView.delegate = self;
    bodyView.userInteractionEnabled = YES;
    bodyView.textColor = color;
    // TODO Figure out font bug and repair LEAK
    bodyView.font = [font retain];
    bodyView.dataDetectorTypes = UIDataDetectorTypeLink;
    bodyView.lineBreakMode = UILineBreakModeWordWrap;
    bodyView.text = text;
    bodyView.layer.shadowColor = [UIColor whiteColor].CGColor;
    bodyView.layer.shadowOpacity = 1;
    bodyView.layer.shadowOffset = CGSizeMake(0, .5);
    bodyView.layer.shadowRadius = 0;
    if (references.count > 0) { 
        NSMutableDictionary* linkAttributes = [NSMutableDictionary dictionary];
        CTFontRef font2 = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", font.pointSize, NULL);
        [linkAttributes setValue:(id)font2 forKey:(NSString*)kCTFontAttributeName];
        CFRelease(font);
        bodyView.linkAttributes = [NSDictionary dictionaryWithDictionary:linkAttributes];
        for (id<STActivityReference> reference in references) {
            if (reference.indices.count == 2) {
                NSInteger start = [[reference.indices objectAtIndex:0] integerValue] + offset;
                NSInteger end = [[reference.indices objectAtIndex:1] integerValue] + offset;
                NSRange range = NSMakeRange(start, end-start);
                NSString* key;
                if (reference.action) {
                    key = [NSString stringWithFormat:@"%d", self.actions.count];
                    [self.actions addObject:reference.action];
                }
                else {
                    key = @"-1";
                }
                [bodyView addLinkToURL:[NSURL URLWithString:key] withRange:range];
            }
        }
    }
    [bodyView sizeToFit];
    [view addSubview:bodyView];
    return CGRectGetMaxX(bodyView.frame);
}

- (id)initWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"test"];
    if (self) {
        actions_ = [[NSMutableArray alloc] init];
        activity_ = [activity retain];
        scope_ = scope;
        _configuration = [[STActivityCellConfiguration alloc] initWithActivity:activity andScope:scope];
        self.accessoryType = UITableViewCellAccessoryNone;
        UIView* imageView = nil;
        if (self.configuration.hasCredit) {
            UIView* background = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, self.configuration.height)] autorelease];
            background.backgroundColor = [UIColor whiteColor];
            [self addSubview:background];
        }
        if (self.configuration.useUserImage && self.activity.subjects.count > 0) {
            id<STUser> user = [self.activity.subjects objectAtIndex:0];
            imageView = [Util profileImageViewForUser:user withSize:self.configuration.imageFrame.size.width];
            imageView.frame = self.configuration.imageFrame;
            [self addSubview:imageView];
            [self addSubview:[Util tapViewWithFrame:imageView.frame target:self selector:@selector(userImageClicked:) andMessage:user]];
        }
        else if (self.activity.image) {
            imageView = [[[UIImageView alloc] initWithFrame:self.configuration.imageFrame] autorelease];
            [[STImageCache sharedInstance] imageForImageURL:self.activity.image andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                [(id)imageView setImage:image]; 
            }];
            [self addSubview:imageView];
        }
        CGFloat y = self.configuration.headerPadding;
        if (self.configuration.header) {
            [self addAttributedText:self.configuration.header
                              frame:CGRectMake(self.configuration.contentOffset, y, self.configuration.headerWidth, self.configuration.headerHeight.floatValue)
                               font:self.configuration.headerFontNormal
                              color:self.configuration.headerColorNormal 
                             offset:0
                         references:self.activity.headerReferences
                             toView:self];
        }
        y += self.configuration.headerHeight.floatValue + self.configuration.bodyPadding;
        if (self.configuration.body) {
            [self addAttributedText:self.configuration.body
                              frame:CGRectMake(self.configuration.contentOffset, y, self.configuration.bodyWidth, self.configuration.bodyHeight.floatValue)
                               font:self.configuration.bodyFontNormal
                              color:self.configuration.bodyColorNormal
                             offset:self.configuration.bodyReferenceOffset
                         references:self.activity.bodyReferences
                             toView:self];
        }
        y += self.configuration.bodyHeight.floatValue + self.configuration.imagesPadding;
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
                        [[STImageCache sharedInstance] imageForImageURL:self.activity.icon andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                            iconImageView.image = image; 
                        }];
                    }
                    [self addSubview:iconImageView];
                }
                [self addSubview:[Util tapViewWithFrame:currentImage.frame target:self selector:@selector(userImageClicked:) andMessage:currentUser]];
            }
            if (self.scope != STStampedAPIScopeYou && users.count == 1) {
                id<STUser> userForDetail = [users objectAtIndex:0];
                CGPoint nameOrigin = CGPointMake(self.configuration.contentOffset + 61, y + 20);
                UIView* nameView = [Util viewWithText:userForDetail.screenName
                                                 font:self.configuration.bodyFontAction
                                                color:self.configuration.bodyColorNormal
                                                 mode:UILineBreakModeTailTruncation
                                           andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
                [Util reframeView:nameView withDeltas:CGRectMake(nameOrigin.x, nameOrigin.y, 0, 0)];
                [self addSubview:nameView];
            }
        }
        y += self.configuration.imagesHeight.floatValue + self.configuration.footerPadding;
        CGFloat timestampX = self.configuration.contentOffset;
        if (self.configuration.footer) {
            timestampX = 11 + [self addAttributedText:self.configuration.footer
                                           frame:CGRectMake(self.configuration.contentOffset, y, self.configuration.footerWidth, self.configuration.footerHeight.floatValue)
                                            font:self.configuration.footerFontNormal
                                           color:self.configuration.footerColorNormal
                                          offset:0
                                      references:self.activity.footerReferences
                                          toView:self];
        }
        UIView* timestampView = [Util viewWithText:[Util userReadableTimeSinceDate:self.activity.created]
                                              font:self.configuration.footerFontTimestamp
                                             color:self.configuration.footerColorTimestamp
                                              mode:UILineBreakModeClip
                                        andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
        [Util reframeView:timestampView withDeltas:CGRectMake(timestampX, y, 0, 0)];
        [self addSubview:timestampView];
        if (!self.configuration.iconOnImages && self.configuration.hasIcon) {
            UIImageView* iconView = [[[UIImageView alloc] initWithFrame:self.configuration.iconFrame] autorelease];
            if (self.configuration.useStampIcon) {
                id<STUser> user = [self.activity.subjects objectAtIndex:0];
                UIImage* stampIcon = [Util stampImageForUser:user withSize:STStampImageSize12];
                iconView.image = stampIcon;
            }
            else {
                [[STImageCache sharedInstance] imageForImageURL:self.activity.icon andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                    iconView.image = image;
                }];
            }
            [self addSubview:iconView];
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
    STActivityCellConfiguration* configuration = [[[STActivityCellConfiguration alloc] initWithActivity:activity andScope:scope] autorelease];
    return configuration.height;
}

@end
