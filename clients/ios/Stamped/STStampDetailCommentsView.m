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
#import "STImageChunk.h"
#import "STAttributedLabel.h"
#import "STUsersViewController.h"
#import "STButton.h"

static const CGFloat _totalWidth = 310;
static const CGFloat _imagePaddingX = 8;
static const CGFloat _imagePaddingY = _imagePaddingX;

static const CGFloat _imageMaxX = 54;
static const CGFloat _bodyX = 64;
static const CGFloat _minimumCellHeight = 64;
static const CGFloat _bodyWidth = 214;

@interface STStampDetailCommentsView () <STAttributedLabelDelegate>

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

+ (UIView*)viewWithUser:(id<STUser>)user 
              isComment:(BOOL)isComment
                 header:(NSString*)header
                   date:(NSDate*)date
                credits:(NSArray<STStampPreview>*)credits 
             references:(NSArray<STActivityReference>*)references
                andBody:(NSString*)body;
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

@interface STStampDetailCommentView : UIView

-(id)initWithComment:(id<STComment>)comment;

@end

@implementation STStampDetailCommentView

- (id)initWithComment:(id<STComment>)comment {
    self = [super initWithFrame:CGRectMake(0, 0, 290, 48)];
    if (self) {
        UIView* userImage = [Util profileImageViewForUser:comment.user withSize:31];
        [Util setTopRightForView:userImage toPoint:CGPointMake(_imageMaxX, 6)];
        [self addSubview:userImage];
        UIView* userButton = [Util tapViewWithFrame:userImage.frame target:self selector:@selector(userImageClicked:) andMessage:comment.user];
        [self addSubview:userButton];
        
        UIView* chunks = [STStampDetailCommentsView viewWithUser:comment.user 
                                                       isComment:YES
                                                          header:nil
                                                            date:[comment created] 
                                                         credits:[NSArray array]
                                                      references:comment.blurbReferences
                                                         andBody:[comment blurb]];
        
        if (chunks.frame.size.height < self.frame.size.height) {
            // TODO setup system for centering chunks
            //chunks.frame = [Util centeredAndBounded:chunks.frame.size inFrame:CGRectMake(0, 0, chunks.frame.size.width, self.frame.size.height)];
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
        UIView* userImage = [Util profileImageViewForUser:stamp.user withSize:46];
        [Util setTopRightForView:userImage toPoint:CGPointMake(_imageMaxX, 6)];
        [self addSubview:userImage];
        UIView* userButton = [Util tapViewWithFrame:userImage.frame target:self selector:@selector(userImageClicked:) andMessage:stamp.user];
        [self addSubview:userButton];
        UIView* lastChunk = nil;
        NSInteger blurbCount = stamp.contents.count;
        if (blurbCount > 0) {
            BOOL first = YES;
            for (NSInteger i = 0; i < blurbCount; i++) {
                id<STContentItem> item = [stamp.contents objectAtIndex:i];
                NSString* header;
                if (!first) {
                    [self insertDots];
                    header = item.blurb ? @" added" : @" stamped again";
                }
                else {
                    NSString* subcategory = stamp.entity.subcategory;
                    header = [NSString stringWithFormat:@" stamped %@", [Util userStringWithBackendType:subcategory andArticle:YES]];
                    first = NO;
                }
                NSArray<STStampPreview>* credits = [NSArray array];
                if (i == blurbCount - 1 && stamp.credits) {
                    credits = stamp.credits;
                }
                UIView* chunks = [STStampDetailCommentsView viewWithUser:stamp.user 
                                                               isComment:NO
                                                                  header:header
                                                                    date:[item created]
                                                                 credits:credits 
                                                              references:[item blurbReferences]
                                                                 andBody:[item blurb]];
                if (blurbCount == 1) {
                    lastChunk = chunks;
                }
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
                            lastChunk = nil;
                        }
                    }
                }
            }
        }
        CGFloat previewHeight = [STPreviewsView previewHeightForStamp:stamp andMaxRows:2];
        if ( previewHeight > 0) {
            lastChunk = nil;
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
        CGFloat minChunkHeight = _minimumCellHeight - 16;
        if (lastChunk && lastChunk.frame.size.height < minChunkHeight) {
            lastChunk.frame = [Util centeredAndBounded:lastChunk.frame.size inFrame:CGRectMake(lastChunk.frame.origin.x,
                                                                                               lastChunk.frame.origin.y,
                                                                                               lastChunk.frame.size.width,
                                                                                               minChunkHeight)];
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
            NSInteger limit = MIN(20, stamp.previews.comments.count);//stamp.previews.comments.count > 3 ? 2 : stamp.previews.comments.count;
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

+ (UIView*)viewWithUser:(id<STUser>)user 
              isComment:(BOOL)isComment
                 header:(NSString*)header
                   date:(NSDate*)date
                credits:(NSArray<STStampPreview>*)credits 
             references:(NSArray<STActivityReference>*)references
                andBody:(NSString*)body {
    CGFloat width = _bodyWidth;
    CGFloat lineHeight = 16;
    
    STChunk* startChunk = [[[STChunk alloc] initWithLineHeight:lineHeight start:0 end:0 width:width lineCount:1 lineLimit:NSIntegerMax] autorelease];
    NSMutableArray* chunks = [NSMutableArray array];
    
    UIFont* userFont = [UIFont stampedBoldFontWithSize:12];
    STTextChunk* userChunk = [[[STTextChunk alloc] initWithPrev:startChunk 
                                                           text:user.screenName
                                                           font:userFont
                                                          color:body ? [UIColor stampedGrayColor] : [UIColor stampedBlackColor]] autorelease];
    [chunks addObject:userChunk];
    
    STChunk* previousChunkForBody = startChunk;
    
    if (header) {
        UIFont* headerFont = [UIFont stampedFontWithSize:12];
        STTextChunk* headerChunk = [[[STTextChunk alloc] initWithPrev:userChunk
                                                                 text:header
                                                                 font:headerFont
                                                                color:body ? [UIColor stampedLightGrayColor] : [UIColor stampedBlackColor]] autorelease];
        [chunks addObject:headerChunk];
        previousChunkForBody = headerChunk;
    }
    
    UIFont* dateFont = [UIFont stampedFontWithSize:10];
    
    STTextChunk* dateChunk = [[[STTextChunk alloc] initWithPrev:startChunk 
                                                           text:[Util shortUserReadableTimeSinceDate:date]
                                                           font:dateFont
                                                          color:[UIColor stampedLightGrayColor]] autorelease];
    dateChunk.topLeft = CGPointMake(235 - dateChunk.end, 0);
    [chunks addObject:dateChunk];
    
    
    //    
    //    STTextChunk* bodyChunk = [[[STTextChunk alloc] initWithPrev:bodyStart
    //                                                           text:body
    //                                                           font:bodyFont
    //                                                          color:[UIColor stampedDarkGrayColor]] autorelease];
    //    [chunks addObject:bodyChunk];
    //
    STAttributedLabel* bodyLabel = nil;
    STChunk* bodyChunk = nil;
    if (body) {
        UIFont* bodyFont = [UIFont stampedFontWithSize:12];
        UIFont* bodyBoldFont = [UIFont stampedBoldFontWithSize:12];
        NSAttributedString* bodyString = [Util attributedStringForString:body
                                                              references:references
                                                                    font:bodyFont
                                                                   color:isComment ? [UIColor stampedDarkGrayColor] : [UIColor stampedBlackColor]
                                                           referenceFont:bodyBoldFont
                                                          referenceColor:[UIColor stampedDarkGrayColor]
                                                              lineHeight:lineHeight
                                                                  indent:0
                                                                 kerning:0];
        STChunk* bodyStart = [STChunk newlineChunkWithPrev:previousChunkForBody];
        bodyChunk = [[[STTextChunk alloc] initWithPrev:bodyStart attributedString:bodyString andPrimaryFont:bodyFont] autorelease];
        bodyLabel = [[[STAttributedLabel alloc] initWithAttributedString:bodyString width:bodyStart.frame.size.width andReferences:references] autorelease];
        bodyLabel.referenceDelegate = (id)self;
        bodyLabel.clipsToBounds = NO;
        [Util reframeView:bodyLabel withDeltas:CGRectMake(0, 3 + bodyChunk.topLeft.y, 0, 0)];
        bodyLabel.userInteractionEnabled = YES;
    }
    NSInteger creditCount = credits.count;
    STButton* creditView = nil;
    if (creditCount > 0) {
        
        UIView* creditViews[2];
        for (NSInteger i = 0; i < 2; i++) {
            BOOL highlight = i == 1;
            UIColor* normalColor = [UIColor stampedGrayColor];
            UIColor* nameColor = [UIColor stampedDarkGrayColor];
            NSMutableArray* creditChunks = [NSMutableArray array];
            CGFloat creditPointSize = 10;
            STChunk* creditStart = [[[STChunk alloc] initWithLineHeight:lineHeight start:0 end:0 width:width lineCount:1 lineLimit:NSIntegerMax] autorelease];
            creditStart = [STChunk newlineChunkWithPrev:creditStart];
            UIFont* creditFont = [UIFont stampedFontWithSize:creditPointSize];
            STTextChunk* creditPrefixChunk = [[[STTextChunk alloc] initWithPrev:creditStart
                                                                           text:@"Credit to "
                                                                           font:creditFont
                                                                          color:normalColor] autorelease];
            
            [creditChunks addObject:creditPrefixChunk];
            
            id<STStampPreview> firstPreview = [credits objectAtIndex:0];
            id<STUser> firstCreditedUser = firstPreview.user;
            UIImage* firstCreditImage = [Util creditImageForUser:user creditUser:firstCreditedUser andSize:STStampImageSize12];
            STImageChunk* firstCreditChunk = [[[STImageChunk alloc] initWithPrev:creditPrefixChunk 
                                                                        andFrame:CGRectMake(0,
                                                                                            3,
                                                                                            firstCreditImage.size.width,
                                                                                            firstCreditImage.size.height)] autorelease];
            firstCreditChunk.image = firstCreditImage;
            
            [creditChunks addObject:firstCreditChunk];
            STTextChunk* firstCreditScreenNameChunk = [[[STTextChunk alloc] initWithPrev:firstCreditChunk
                                                                                    text:[NSString stringWithFormat:@" %@", firstCreditedUser.screenName]
                                                                                    font:[UIFont stampedBoldFontWithSize:creditPointSize]
                                                                                   color:nameColor] autorelease];
            [creditChunks addObject:firstCreditScreenNameChunk];
            
            if (creditCount > 1) {
                STTextChunk* andChunk = [[[STTextChunk alloc] initWithPrev:firstCreditScreenNameChunk
                                                                      text:@" and "
                                                                      font:[UIFont stampedFontWithSize:creditPointSize]
                                                                     color:normalColor] autorelease];
                [creditChunks addObject:andChunk];
                if (creditCount == 2) {
                    id<STStampPreview> secondPreview = [credits objectAtIndex:1];
                    id<STUser> secondUser = secondPreview.user;
                    //UIImage* secondCreditImage = [Util creditImageForUser:user creditUser:secondUser andSize:STStampImageSize12];
                    //STImageChunk* secondImageChunk = [[[STImageChunk alloc] initWithPrev:andChunk andFrame:CGRectMake(0,3, secondCreditImage.size.width, secondCreditImage.size.height)] autorelease];
                    //secondImageChunk.image = secondCreditImage;
                    //[chunks addObject:secondImageChunk];
                    STTextChunk* secondScreenNameChunk = [[[STTextChunk alloc] initWithPrev:andChunk
                                                                                       text:[NSString stringWithFormat:@"%@", secondUser.screenName]
                                                                                       font:[UIFont stampedBoldFontWithSize:creditPointSize]
                                                                                      color:nameColor] autorelease];
                    [creditChunks addObject:secondScreenNameChunk];
                }
                else {
                    STTextChunk* others = [[[STTextChunk alloc] initWithPrev:andChunk
                                                                        text:[NSString stringWithFormat:@"%d others", creditCount - 1]
                                                                        font:[UIFont stampedBoldFontWithSize:creditPointSize]
                                                                       color:nameColor] autorelease];
                    [creditChunks addObject:others];
                }
            }
            STChunksView* creditChunksView = [[[STChunksView alloc] initWithChunks:creditChunks] autorelease];
            if (highlight) {
                creditChunksView.alpha = .5;
            }
            creditViews[i] = creditChunksView;
        }
        creditView = [[[STButton alloc] initWithFrame:creditViews[0].frame 
                                           normalView:creditViews[0] 
                                           activeView:creditViews[1]
                                               target:self andAction:@selector(creditsClicked:)] autorelease];
        creditView.message = credits;
    }
    
    STChunksView* view = [[[STChunksView alloc] initWithChunks:chunks] autorelease];
    if (bodyLabel) {
        CGRect frame = view.frame;
        frame.size.height =  MAX(CGRectGetMaxY(bodyLabel.frame), frame.size.height);
        view.frame = frame;
        [view addSubview:bodyLabel];
    }
    if (creditView) {
        [Util appendView:creditView toParentView:view];
    }
    //NSLog(@"ChunkHeight:%f",view.frame.size.height);
    //    if (creditCount) {
    //        CGFloat y = bodyChunk ? CGRectGetMaxY(bodyChunk.frame) : CGRectGetMaxY(userChunk.frame);
    //        CGRect creditFrame = CGRectMake(0, y, width, view.frame.size.height - y);
    //        UIView* creditButton = [Util tapViewWithFrame:creditFrame andCallback:^{
    //            if (credits.count == 1) {
    //                id<STStampPreview> first = [credits objectAtIndex:0];
    //                [[STStampedActions sharedInstance] viewStampWithStampID:first.stampID];
    //            }
    //            else {
    //                NSMutableArray* userIDs = [NSMutableArray array];
    //                NSMutableDictionary* mapping = [NSMutableDictionary dictionary];
    //                for (id<STStampPreview> preview in credits) {
    //                    NSString* userID = preview.user.userID;
    //                    if (userID) {
    //                        [userIDs addObject:userID];
    //                        if (preview.stampID) {
    //                            [mapping setObject:preview.stampID forKey:userID];
    //                        }
    //                    }
    //                }
    //                STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:userIDs] autorelease];
    //                controller.userIDToStampID = mapping;
    //                [[Util sharedNavigationController] pushViewController:controller animated:YES];
    //            }
    //        }];
    //        [view addSubview:creditButton];
    //    }
    return view;
}

+ (void)creditsClicked:(NSArray<STStampPreview>*)credits {
    if (credits.count == 1) {
        id<STStampPreview> first = [credits objectAtIndex:0];
        [[STStampedActions sharedInstance] viewStampWithStampID:first.stampID];
    }
    else {
        NSMutableArray* userIDs = [NSMutableArray array];
        NSMutableDictionary* mapping = [NSMutableDictionary dictionary];
        for (id<STStampPreview> preview in credits) {
            NSString* userID = preview.user.userID;
            if (userID) {
                [userIDs addObject:userID];
                if (preview.stampID) {
                    [mapping setObject:preview.stampID forKey:userID];
                }
            }
        }
        STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:userIDs] autorelease];
        controller.userIDToStampID = mapping;
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
    }
}

+ (void)attributedLabel:(STAttributedLabel *)label didSelectReference:(id<STActivityReference>)reference {
    id<STAction> action = reference.action;
    if (action) {
        
        [[STActionManager sharedActionManager] didChooseAction:action withContext:[STActionContext context]];
    }
}

@end
