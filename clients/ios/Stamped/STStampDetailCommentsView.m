//
//  STStampDetailCommentsView.m
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailCommentsView.h"
#import "UserImageView.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STImageView.h"
#import "STSimpleUser.h"
#import "STStampedAPI.h"
#import "STRippleBar.h"
#import "STUserViewController.h"
#import "STPreviewsView.h"
#import "STChunksView.h"
#import "STTextChunk.h"
#import "STImageCache.h"
#import "STPhotoViewController.h"
#import "STActionManager.h"
#import "STStampedActions.h"

static const CGFloat _totalWidth = 310;
static const CGFloat _imagePaddingX = 8;
static const CGFloat _imagePaddingY = _imagePaddingX;

static const CGFloat _imageMaxX = 54;
static const CGFloat _bodyX = 64;
static const CGFloat _minimumCellHeight = 64;
static const CGFloat _bodyWidth = 214;

@interface STStampDetailCommentsView ()

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

+ (UIView*)viewWithUser:(id<STUser>)user header:(NSString*)header date:(NSDate*)date andBody:(NSString*)body;

@end

@interface STStampDetailBarView : UIView

@end

@implementation STStampDetailBarView

- (id)init {
    self = [super initWithFrame:CGRectMake(0, 0, _totalWidth, 1)];
    if (self) {
        self.backgroundColor = [UIColor colorWithWhite:.90 alpha:1];
    }
    return self;
}

@end

@interface STAStampDetailCommentView : UIView

- (id)initWithUser:(id<STUser>)user andProfileImageSize:(STProfileImageSize)size;

@property (nonatomic, readonly, retain) UIView* userImage;

@end

@implementation STAStampDetailCommentView

@synthesize userImage = _userImage;

- (id)initWithUser:(id<STUser>)user andProfileImageSize:(STProfileImageSize)size {
    self = [super initWithFrame:CGRectMake(0, 0, _totalWidth, size + 2 * _imagePaddingY)];
    if (self) {
        UIView* imageView = [Util profileImageViewForUser:user withSize:size];
        [Util reframeView:imageView withDeltas:CGRectMake(_imagePaddingX, _imagePaddingY, 0, 0)];
        [self addSubview:imageView];
        UIView* imageButton = [Util tapViewWithFrame:imageView.frame target:self selector:@selector(userImageClicked:) andMessage:user];
        [self addSubview:imageButton];
        _userImage = [imageView retain];
    }
    return self;
}

- (void)userImageClicked:(id<STUser>)user {
    STUserViewController* controller = [[[STUserViewController alloc] initWithUser:user] autorelease];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
}

- (void)dealloc
{
    [_userImage release];
    [super dealloc];
}

/*
 TODO
 - (void)userImageTapped:(id)button {
 STActionContext* context = [STActionContext context];
 id<STAction> action = [STStampedActions actionViewUser:self.user.userID withOutputContext:context];
 [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
 NSLog(@"action not enabled");
 }
 */

@end

@interface STAStampDetailCommentWithText : STAStampDetailCommentView

- (id)initWithUser:(id<STUser>)user 
           created:(NSDate*)created 
              text:(NSString*)text 
andProfileImageSize:(STProfileImageSize)size;

@property (nonatomic, readonly, retain) UIView* userNameView;
@property (nonatomic, readonly, retain) UIView* dateView;
@property (nonatomic, readonly, retain) UIView* blurbView;

@end

@implementation STAStampDetailCommentWithText

@synthesize userNameView = _userNameView;
@synthesize dateView = _dateView;
@synthesize blurbView = _blurbView;

- (id)initWithUser:(id<STUser>)user  
           created:(NSDate*)created 
              text:(NSString*)text 
andProfileImageSize:(STProfileImageSize)size {
    self = [super initWithUser:user andProfileImageSize:size];
    if (self) {
        CGFloat boundsX = CGRectGetMaxX(self.userImage.frame) + 5;
        CGFloat dateX = _totalWidth - 30;
        CGRect textBounds = CGRectMake( boundsX, self.userImage.frame.origin.y, dateX - boundsX , CGFLOAT_MAX);
        UIFont* userNameFont = size == STProfileImageSize31 ? [UIFont stampedBoldFontWithSize:14] : [UIFont stampedBoldFontWithSize:16];
        _userNameView = [[Util viewWithText:user.screenName 
                                       font:userNameFont 
                                      color:[UIColor stampedGrayColor] 
                                       mode:UILineBreakModeClip 
                                 andMaxSize:textBounds.size] retain];
        _userNameView.frame = CGRectOffset(_userNameView.frame, textBounds.origin.x, textBounds.origin.y);
        [self addSubview:_userNameView];
        
        UIFont* dateFont = size == STProfileImageSize31 ? [UIFont stampedFontWithSize:12] : [UIFont stampedFontWithSize:14];
        _dateView = [[Util viewWithText:[Util shortUserReadableTimeSinceDate:created]
                                   font:dateFont 
                                  color:[UIColor stampedLightGrayColor] 
                                   mode:UILineBreakModeClip 
                             andMaxSize:CGSizeMake(30, 25)] retain];
        _dateView.frame = CGRectOffset(_dateView.frame, dateX, textBounds.origin.y);
        [self addSubview:_dateView];
        textBounds.origin.y = CGRectGetMaxY(_userNameView.frame) + 2;
        
        
        _blurbView = [[Util viewWithText:(text ? text : @" ")
                                    font:[UIFont stampedFontWithSize:14]  
                                   color:[UIColor stampedDarkGrayColor] 
                                    mode:UILineBreakModeWordWrap 
                              andMaxSize:textBounds.size] retain];
        _blurbView.frame = CGRectOffset(_blurbView.frame, textBounds.origin.x, textBounds.origin.y);
        [self addSubview:_blurbView];
        
        CGRect frame = self.frame;
        frame.size.height = MAX(CGRectGetMaxY(self.userImage.frame), CGRectGetMaxY(self.blurbView.frame))+5;
        self.frame = frame;
    }
    return self;
}

- (void)dealloc {
    [_blurbView release];
    [_userNameView release];
    [_dateView release];
    [super dealloc];
}

@end

@interface STStampDetailCommentView : UIView

-(id)initWithComment:(id<STComment>)comment;

@end

@implementation STStampDetailCommentView

- (id)initWithComment:(id<STComment>)comment {
    self = [super initWithFrame:CGRectMake(0, 0, 290, 48)];
    if (self) {
        UIView* userImage = [Util profileImageViewForUser:comment.user withSize:STProfileImageSize31];
        [Util setTopRightForView:userImage toPoint:CGPointMake(_imageMaxX, 6)];
        [self addSubview:userImage];
        UIView* userButton = [Util tapViewWithFrame:userImage.frame target:self selector:@selector(userImageClicked:) andMessage:comment.user];
        [self addSubview:userButton];
        
        UIView* chunks = [STStampDetailCommentsView viewWithUser:comment.user
                                                          header:nil
                                                            date:[comment created]
                                                         andBody:[comment blurb]];
        
        if (chunks.frame.size.height < self.frame.size.height) {
            chunks.frame = [Util centeredAndBounded:chunks.frame.size inFrame:CGRectMake(0, 0, chunks.frame.size.width, self.frame.size.height)];
        }
        [Util reframeView:chunks withDeltas:CGRectMake(_bodyX, 0, 0, 0)];
        [self addSubview:chunks];
        
        CGRect finalFrame = self.frame;
        finalFrame.size.height = MAX(finalFrame.size.height, CGRectGetMaxY(chunks.frame) + 12);
        self.frame = finalFrame;
    }
    return self;
}

- (void)userImageClicked:(id<STUser>)user {
    STActionContext* context = [STActionContext contextInView:self];
    id<STAction> action = [STStampedActions actionViewUser:user.userID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

@end

@interface STStampDetailBlurbView : STViewContainer

- (id)initWithStamp:(id<STStamp>)stamp andDelegate:(id<STViewDelegate>)delegate;

@property (nonatomic, readonly, copy) NSString* imageURL;

@end

@implementation STStampDetailBlurbView

@synthesize imageURL = imageURL_;

- (void)viewURL:(NSString*)url {
    STPhotoViewController *controller = [[[STPhotoViewController alloc] initWithURL:[NSURL URLWithString:url]] autorelease];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
}

- (void)userImageClicked:(id<STUser>)user {
    STActionContext* context = [STActionContext contextInView:self];
    id<STAction> action = [STStampedActions actionViewUser:user.userID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (id)initWithStamp:(id<STStamp>)stamp andDelegate:(id<STViewDelegate>)delegate {
    self = [super initWithDelegate:delegate andFrame:CGRectMake(0, 0, 290, 0)];
    if (self) {
        UIView* userImage = [Util profileImageViewForUser:stamp.user withSize:STProfileImageSize46];
        [Util setTopRightForView:userImage toPoint:CGPointMake(_imageMaxX, 6)];
        [self addSubview:userImage];
        UIView* userButton = [Util tapViewWithFrame:userImage.frame target:self selector:@selector(userImageClicked:) andMessage:stamp.user];
        [self addSubview:userButton];
        
        NSInteger blurbCount = stamp.contents.count;
        if (blurbCount > 0) {
            BOOL first = YES;
            for (NSInteger i = blurbCount - 1; i >= 0; i--) {
                NSString* header;
                if (!first) {
                    [self insertDots];
                    header = @" added";
                }
                else {
                    NSString* subcategory = stamp.entity.subcategory;
                    NSString* formatString;
                    NSSet* vowels = [NSSet setWithObjects:@"a", @"e", @"i", @"o", @"u", nil];
                    if ([vowels containsObject:[subcategory substringToIndex:1]]) {
                        formatString = @" stamped an %@";
                    }
                    else {
                        formatString = @" stamped a %@";
                    }
                    header = [NSString stringWithFormat:formatString, subcategory];
                    first = NO;
                }
                id<STContentItem> item = [stamp.contents objectAtIndex:i];
                UIView* chunks = [STStampDetailCommentsView viewWithUser:stamp.user
                                                                  header:header
                                                                    date:[item created]
                                                                 andBody:[item blurb]];
                [Util reframeView:chunks withDeltas:CGRectMake(_bodyX, 0, 0, 0)];
                [self appendChildView:chunks];
                if (item.images.count) {
                    id<STImageList> imageList = [item.images objectAtIndex:0];
                    NSArray* sizes = imageList.sizes;
                    if (sizes.count) {
                        CGSize size;
                        NSString* url = nil;
                        for (id<STImage> image in sizes) {
                            if (image.height && image.width && image.url) {
                                CGSize curSize = CGSizeMake(image.width.floatValue, image.height.floatValue);
                                if (!url || curSize.width > size.width) {
                                    size = curSize;
                                    url = image.url;   
                                }
                            }
                        }
                        if (url) {
                            size.width /= [Util imageScale];
                            size.height /= [Util imageScale];
                            CGRect imageFrame = [Util centeredAndBounded:size inFrame:CGRectMake(_bodyX, 0, _bodyWidth, size.height)];
                            imageFrame.origin.y = 0;
                            UIImageView* imageView = [[[UIImageView alloc] initWithFrame:imageFrame] autorelease];
                            CALayer* gradient = [Util addGradientToLayer:imageView.layer withColors:[UIColor stampedDarkGradient] vertical:YES];
                            [[STImageCache sharedInstance] imageForImageURL:url andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                                imageView.image = image;
                                [gradient removeFromSuperlayer];
                            }];
                            UIView* imageButton = [Util tapViewWithFrame:CGRectMake(0, 0, imageFrame.size.width, imageFrame.size.height) 
                                                                  target:self 
                                                                selector:@selector(viewURL:)
                                                              andMessage:url];
                            imageView.userInteractionEnabled = YES;
                            [imageView addSubview:imageButton];
                            [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 12)];
                            [self appendChildView:imageView];
                        }
                    }
                }
            }
        }
        CGFloat previewHeight = [STPreviewsView previewHeightForStamp:stamp andMaxRows:2];
        if ( previewHeight > 0) {
            [self insertDots];
            [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 5)];
            STPreviewsView *view = [[[STPreviewsView alloc] initWithFrame:CGRectZero] autorelease];
            [view setupWithStamp:stamp maxRows:2];
            CGRect frame = view.frame;
            frame.origin.x = _bodyX;
            //frame.origin.y = self.frame.size.height;
            //frame.size.height += previewHeight;
            view.frame = frame;
            [self appendChildView:view];
        }
        else {
            [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 16)];
        }
        
        CGRect finalFrame = self.frame;
        finalFrame.size.height = MAX(finalFrame.size.height, _minimumCellHeight);
        self.frame = finalFrame;
    }
    return self;
}

- (void)insertDots {
    UIImageView* dotsView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"TEMP_sDetail_dots"]] autorelease];
    [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 14 - dotsView.frame.size.height)];
    [Util reframeView:dotsView withDeltas:CGRectMake(_bodyX, 0, 0, 0)];
    [self appendChildView:dotsView];
}

- (void)imageClicked:(id)notImportant {
    if (self.imageURL) {
        
    }
}

- (void)dealloc {
    [imageURL_ release];
    [super dealloc];
}

@end

@implementation STStampDetailCommentsView

@synthesize stamp = stamp_;

- (void)setStamp:(id<STStamp>)stamp {
    if (!stamp_ || ![stamp_.modified isEqualToDate:stamp.modified]) {
        BOOL first = stamp_ == nil;
        [stamp_ autorelease];
        stamp_ = [stamp retain];
        CGFloat heightBefore = self.frame.size.height;
        for (UIView* view in [NSArray arrayWithArray:self.subviews]) {
            [view removeFromSuperview];
        }
        [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, -self.frame.size.height)];
        [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 2)];
        
        STRippleBar* topBar = [[[STRippleBar alloc] initWithPrimaryColor:stamp.user.primaryColor andSecondaryColor:stamp.user.secondaryColor isTop:YES] autorelease];
        [self appendChildView:topBar];
        
        UIView* blurbView = [[[STStampDetailBlurbView alloc] initWithStamp:stamp andDelegate:self] autorelease];
        [self appendChildView:blurbView];
        if (index == 0 || YES) {
            NSInteger limit = stamp.previews.comments.count > 3 ? 2 : stamp.previews.comments.count;
            for (NSInteger i = 0; i < limit; i++) {
                NSInteger index = limit - (i + 1);
                id<STComment> comment = [stamp.previews.comments objectAtIndex:index];
                if (i == 0) {
                    [self appendChildView:[[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"TEMP_blurbView_keyline"]] autorelease]];
                }
                else {
                    [self appendChildView:[[[STStampDetailBarView alloc] init] autorelease]];
                }
                STStampDetailCommentView* commentView = [[[STStampDetailCommentView alloc] initWithComment:comment] autorelease];
                [self appendChildView:commentView];
            }
        }
        STRippleBar* bottomBar = [[[STRippleBar alloc] initWithPrimaryColor:stamp.user.primaryColor andSecondaryColor:stamp.user.secondaryColor isTop:NO] autorelease];
        [self appendChildView:bottomBar];
        [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 2)];
        
        if (!first) {
            CGFloat heightDelta = self.frame.size.height - heightBefore;
            [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, -heightDelta)];
            self.clipsToBounds = YES;
            [self.delegate childView:self shouldChangeHeightBy:heightDelta overDuration:.25];
        }
        self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
    }
}

- (id)initWithStamp:(id<STStamp>)stamp andDelegate:(id<STViewDelegate>)delegate {
    CGFloat width = _totalWidth;
    CGFloat padding_x = 5;
    self = [super initWithDelegate:delegate andFrame:CGRectMake(padding_x, 0, width, 0)];
    if (self) {
        self.backgroundColor = [UIColor whiteColor];
        
        self.layer.shadowColor = [UIColor blackColor].CGColor;
        self.layer.shadowOpacity = .2;
        self.layer.shadowRadius = 2.5;
        self.layer.shadowOffset = CGSizeMake(0, 5);
        
        [self setStamp:stamp];
    }
    return self;
}

- (void)dealloc {
    [stamp_ release];
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)reloadStampedData {
    [[STStampedAPI sharedInstance] stampForStampID:self.stamp.stampID andCallback:^(id<STStamp> stamp, NSError *error, STCancellation *cancellation) {
        if (stamp) {
            self.stamp = stamp;
        }
    }];
}

+ (UIView*)viewWithUser:(id<STUser>)user header:(NSString*)header date:(NSDate*)date andBody:(NSString*)body {
    
    CGFloat width = _bodyWidth;
    CGFloat lineHeight = 16;
    
    STChunk* startChunk = [[[STChunk alloc] initWithLineHeight:lineHeight start:0 end:0 width:width lineCount:1 lineLimit:NSIntegerMax] autorelease];
    NSMutableArray* chunks = [NSMutableArray array];
    
    UIFont* userFont = [UIFont stampedBoldFontWithSize:10];
    STTextChunk* userChunk = [[[STTextChunk alloc] initWithPrev:startChunk 
                                                           text:user.screenName
                                                           font:userFont
                                                          color:[UIColor stampedGrayColor]] autorelease];
    [chunks addObject:userChunk];
    
    if (header) {
        UIFont* headerFont = [UIFont stampedFontWithSize:10];
        STTextChunk* headerChunk = [[[STTextChunk alloc] initWithPrev:userChunk
                                                                 text:header
                                                                 font:headerFont
                                                                color:[UIColor stampedLightGrayColor]] autorelease];
        [chunks addObject:headerChunk];
    }
    
    UIFont* dateFont = [UIFont stampedFontWithSize:10];
    
    STTextChunk* dateChunk = [[[STTextChunk alloc] initWithPrev:startChunk 
                                                           text:[Util shortUserReadableTimeSinceDate:date]
                                                           font:dateFont
                                                          color:[UIColor stampedLightGrayColor]] autorelease];
    dateChunk.topLeft = CGPointMake(235 - dateChunk.end, 0);
    [chunks addObject:dateChunk];
    
    STChunk* bodyStart = [STChunk newlineChunkWithPrev:startChunk];
    
    UIFont* bodyFont = [UIFont stampedFontWithSize:12];
    STTextChunk* bodyChunk = [[[STTextChunk alloc] initWithPrev:bodyStart
                                                           text:body
                                                           font:bodyFont
                                                          color:[UIColor stampedDarkGrayColor]] autorelease];
    [chunks addObject:bodyChunk];
    
    STChunksView* view = [[[STChunksView alloc] initWithChunks:chunks] autorelease];
    //NSLog(@"ChunkHeight:%f",view.frame.size.height);
    return view;
}

@end
