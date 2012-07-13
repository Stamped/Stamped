//
//  STStampCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampCell.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "TTTAttributedLabel.h"
#import "STPreviewsView.h"
#import "STConfiguration.h"
#import "STBlockUIView.h"
#import <QuartzCore/QuartzCore.h>
#import "STImageCache.h"
#import "QuartzUtils.h"
#import "STSimpleStamp.h"
#import "STDetailTextCallout.h"
#import "ImageLoader.h"
#import "STAvatarView.h"
#import "STUserImageView.h"

@interface STStampCell ()

@property (nonatomic, readonly, retain) STUserImageView* userImageView;
@property (nonatomic, readwrite, retain) STCancellation* userImageCancellation;
@property (nonatomic, readwrite, retain) id<STStamp> stamp;

@end

@implementation STStampCell

@synthesize stamp = _stamp;
@synthesize username=_username;
@synthesize subcategory=_subcategory;
@synthesize title=_title;
@synthesize category=_category;
@synthesize identifier=_identifier;
@synthesize commentCount=_commentCount;
@synthesize delegate;
@synthesize userImageView = _userImageView;
@synthesize userImageCancellation = _userImageCancellation;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier])) {
        
        self.accessoryType = UITableViewCellAccessoryNone;
        
        CGFloat originY = 10.0f;
        UIImage *image = [UIImage imageNamed:@"stamp_cell_shadow_footer.png"];
        UIImageView *footer = [[[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]] autorelease];
        footer.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
        CGRect frame = footer.frame;
        frame.size.width = self.frame.size.width;
        frame.origin.y = floorf(self.bounds.size.height-frame.size.height);
        footer.frame = frame;
        
        [self addSubview:footer];
        
        
        _footerImageView = footer;
        
        // user image view
        
        _userImageView = [[STUserImageView alloc] initWithSize:48];//[[Util profileImageViewForUser:nil withSize:46] retain]; //[[UIImageView alloc] initWithFrame:CGRectMake(11.0f, originY, 46.0f, 46.0f)];
        [Util reframeView:_userImageView withDeltas:CGRectMake(11, originY, 0, 0)];
        [self addSubview:_userImageView];
        
        UILongPressGestureRecognizer *longPress = [[UILongPressGestureRecognizer alloc] initWithTarget:self action:@selector(longPress:)];
        longPress.minimumPressDuration = 1.5f;
        [self addGestureRecognizer:longPress];
        [longPress release];
        
        // cell text
        STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:CGRectMake(68, 0, self.bounds.size.width - 88.0f, 70.0f + originY)];
        view.backgroundColor = [UIColor whiteColor];
        [self addSubview:view];
        [view setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            
            BOOL highlighted = self.highlighted || self.selected;
            
            if (_username && _subcategory) {
                [highlighted ? [UIColor whiteColor] : [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f] setFill];
                UIFont *font = [UIFont stampedBoldFontWithSize:12];
                CGSize size = [_username sizeWithFont:font];
                [_username drawInRect:CGRectMake(rect.origin.x, rect.origin.y + 5.5, size.width, size.height) withFont:font lineBreakMode:UILineBreakModeTailTruncation];
                [_subcategory drawAtPoint:CGPointMake(size.width, rect.origin.y + 6.0 ) withFont:[UIFont stampedFontWithSize:12]];
            }
            
            if (_category) {
                if (_categoryImage) {
                    CGFloat imageOffset = 13;
                    if (highlighted) {
                        
                        CGContextSaveGState(ctx);
                        CGRect imageRect = CGRectMake(rect.origin.x, rect.size.height -  (56.0f+_categoryImage.size.height + imageOffset), _categoryImage.size.width, _categoryImage.size.height);
                        CGContextTranslateCTM(ctx, 0, rect.size.height);
                        CGContextScaleCTM(ctx, 1.0, -1.0);
                        
                        [[UIColor whiteColor] setFill];
                        CGContextClipToMask(ctx, imageRect, _categoryImage.CGImage);
                        
                        CGContextFillRect(ctx, imageRect);
                        CGContextRestoreGState(ctx);
                        
                    } else {
                        [_categoryImage drawAtPoint:CGPointMake(rect.origin.x, 56.0f + imageOffset)];
                    }
                    
                }
                [highlighted ? [UIColor whiteColor] : [UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f] setFill];
                [_category drawAtPoint:CGPointMake((_categoryImage!=nil) ? _categoryImage.size.width + 5.0f : 0.0f, 54.0f + 12) withFont:[UIFont stampedFontWithSize:12]];
            }
            
            if (_title) {
                
                UIFont *font = [UIFont stampedTitleLightFontWithSize:40];
                CGContextSetFillColorWithColor(ctx, [highlighted ? [UIColor whiteColor] : [UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:1.0f] CGColor]);
                
                CGContextSetCharacterSpacing(ctx, 10);
                CGPoint point = CGPointMake(0.0f, 18.0f + 7.5f); //adjusted
                CGFloat maxWidth = rect.size.width - 36.0f - 10;
                BOOL _drawn = NO;
                BOOL truncate = NO;
                
                for (NSInteger i = 0; i < _title.length; i++) {
                    
                    NSString *subString = [_title substringWithRange:NSMakeRange(i, 1)];
                    CGSize size = [subString sizeWithFont:font];
                    CGFloat originX = floorf(point.x + (size.width + 1.5));
                    
                    // draw stamp at the last shown char
                    if (!_drawn && (truncate || i == _title.length-1)) {
                        _drawn = YES;
                        
                        CGFloat imageOrigin = MIN(floorf(originX - 7), rect.size.width-14.0f);
                        if (truncate && i < _title.length-1) {
                            if ([[_title substringWithRange:NSMakeRange(i, 1)] isEqualToString:@" "]) {
                                imageOrigin -= size.width;
                            }
                        }
                        // 31 , 32
                        // 29 , 24
                        CGRect imageRect = CGRectMake(imageOrigin, 17.0f, 18.0f, 18.0f);
                        imageRect.origin.y = floorf(rect.size.height - (17.0f+18.0f) ) - 13;
                        imageRect.origin.y += 4;
                        imageRect.origin.x += 1;
                        CGContextSaveGState(ctx);
                        CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
                        CGContextScaleCTM(ctx, 1.0f, -1.0f);
                        CGContextClipToMask(ctx, imageRect, [UIImage imageNamed:@"stamp_18pt_texture.png"].CGImage);
                        
                        if (self.highlighted) {
                            
                            [[UIColor whiteColor] setFill];
                            CGContextFillRect(ctx, imageRect);
                            
                        } else {
                            
                            rect = CGContextGetClipBoundingBox(ctx);
                            CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
                            size_t _numLocations = 2;
                            CGFloat _locations[2] = { 0.0, 1.0 };
                            CGFloat _colors[8] = { r, g, b, 1, r1, g1, b1, 1 };
                            CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
                            CGColorSpaceRelease(_rgb);
                            CGPoint start = CGPointMake(rect.origin.x, rect.origin.y + rect.size.height);
                            CGPoint end = CGPointMake(rect.origin.x + rect.size.width, rect.origin.y);
                            CGContextDrawLinearGradient(ctx, gradient, start, end, kCGGradientDrawsAfterEndLocation);
                            CGGradientRelease(gradient);
                            
                        }
                        
                        CGContextRestoreGState(ctx);
                        
                    }
                    [subString drawAtPoint:point withFont:font];
                    
                    CGContextShowTextAtPoint(ctx, point.x, point.y, "Test", 4);
                    point.x = originX;
                    
                    if (truncate) {
                        if ([subString isEqualToString:@" "]) {
                            point.x -= size.width;
                        }
                        [@"..." drawAtPoint:point withFont:font];
                        break;
                    }
                    
                    truncate = (point.x >= maxWidth && i != _title.length-2);
                    
                }
                
            }
            
        }];
        _headerView = view;
        [view release];
        
        // date label
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.font = [UIFont stampedFontWithSize:10];
        label.textColor = [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        label.backgroundColor = [UIColor whiteColor];
        [self addSubview:label];
        _dateLabel = label;
        [label release];
        
        STPreviewsView *previewsView = [[STPreviewsView alloc] initWithFrame:CGRectMake(69.0f, 95.0f - 2, 0, 0)];
        [self addSubview:previewsView];
        _statsView = previewsView;
        [previewsView release];
        _statsView.hidden = YES;
        
        CAShapeLayer *layer = [CAShapeLayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.fillColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor;
        layer.strokeColor = [UIColor colorWithRed:0.8509f green:0.8509f blue:0.8509f alpha:1.0f].CGColor;
        layer.lineDashPattern = [NSArray arrayWithObjects:[NSNumber numberWithFloat:1], [NSNumber numberWithFloat:2], nil];
        layer.frame = CGRectMake(70.0f, 88.0f, self.bounds.size.width - 80.0f, 1.0f);
        layer.path = [UIBezierPath bezierPathWithRect:layer.bounds].CGPath;
        layer.strokeEnd = .5;
        [self.layer addSublayer:layer];
        _statsDots = layer;
        
        // comment count
        STBlockUIView *commentView = [[STBlockUIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, 200, 60.0f)];
        commentView.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin;
        commentView.backgroundColor = [UIColor whiteColor];
        [self addSubview:commentView];
        [commentView setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            
            BOOL highlighted = self.highlighted || self.selected;
            
            CGFloat offset = 0.0f;
            if (_commentCount > 0) {
                
                UIImage *image = [UIImage imageNamed:highlighted ? @"stamp_cell_comment_hi.png" : @"stamp_cell_comment.png"];
                [image drawAtPoint:CGPointMake(0, 1.0f)];
                
                offset += 12.0f;
                if (!_hasMedia) {
                    
                    [highlighted ? [UIColor whiteColor] : [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f] setFill];
                    NSString *comments = [NSString stringWithFormat:@"%i", _commentCount];
                    CGFloat width = [[NSString stringWithFormat:@"%i", self.commentCount] sizeWithFont:[UIFont stampedFontWithSize:12]].width;
                    UIFont *font = [UIFont stampedFontWithSize:12];
                    [comments drawInRect:CGRectMake(offset, -1.0f, width, font.lineHeight) withFont:font];
                    offset += (width+2.0f);
                }
            }
            
            if (_hasMedia) {
                [[UIImage imageNamed:self.highlighted ? @"stamp_cell_media_hi.png" : @"stamp_cell_media.png"] drawAtPoint:CGPointMake(offset, 0.0f)];
            }
            
        }];
        [commentView release];
        _commentView = commentView;
        
    }
    return self;
}

- (void)dealloc {
    
    [_categoryImage release], _categoryImage=nil;
    [_category release], _category=nil;
    [_title release], _title = nil;
    [_username release], _username = nil;
    [_subcategory release], _subcategory = nil;
    [_primaryColor release], _primaryColor = nil;
    [_secondarayColor release], _secondarayColor = nil;
    [_userImageCancellation cancel];
    [_userImageCancellation release];
    [_userImageView release];
    _statsView = nil;
    _dateLabel = nil;
    [_stamp release];
    [super dealloc];
    
}

-(void)prepareForReuse {
    [self.userImageCancellation cancel];
    self.userImageCancellation = nil;
    self.userImageView.image = nil;
}

- (void)setupWithStamp:(id<STStamp>)stamp {
    self.stamp = stamp;
    if (_cancellation) {
        [_cancellation cancel];
        _cancellation = nil;
    }
    
    [_category release], _category=nil;
    _category = [stamp.entity.subtitle copy];
    
    [_title release], _title = nil;
    _title = [stamp.entity.title copy];
    
    [_username release], _username = nil;
    _username = [stamp.user.screenName copy];
    
    [_subcategory release], _subcategory = nil;
    _subcategory =  [[NSString stringWithFormat:@" stamped %@", [Util userStringWithBackendType:stamp.entity.subcategory andArticle:YES]] copy];
    
    [_categoryImage release], _categoryImage=nil;
    UIImage* catIcon = [Util categoryIconForCategory:stamp.entity.category subcategory:stamp.entity.subcategory filter:nil andSize:STCategoryIconSize9];
    catIcon = [Util gradientImage:catIcon withPrimaryColor:@"b2b2b2" secondary:@"999999" andStyle:STGradientStyleVertical];
    _categoryImage = [catIcon retain];
    
    [Util splitHexString:stamp.user.primaryColor toRed:&r green:&g blue:&b];
    [Util splitHexString:stamp.user.secondaryColor toRed:&r1 green:&g1 blue:&b1];
    
    _commentCount = [stamp.numComments integerValue];
    for (id obj in stamp.contents) {
        _hasMedia = [[obj images] count] > 0;
        if (_hasMedia) {
            break;
        }
    }
    
    // stats previews
    _statsView.hidden = ([STPreviewsView previewHeightForStamp:stamp andMaxRows:1] <= 0.0f);
    _footerImageView.hidden = _statsView.hidden;
    _statsDots.hidden = _statsView.hidden;
    if (!_statsView.hidden) {
        [_statsView setupWithStamp:stamp maxRows:1];
    }
    
    _commentView.hidden = (_commentCount==0 && !_hasMedia);
    if (!_commentView.hidden) {
        CGRect frame = _commentView.frame;
        frame.size.width = 0.0f;
        frame.size.height = 10.0f;
        if (_hasMedia) {
            frame.size.width += 10.0f;
        }
        if (_commentCount > 0) {
            frame.size.width += 12.0f;
            if (!_hasMedia) {
                frame.size.width += [[NSString stringWithFormat:@"%i", self.commentCount] sizeWithFont:[UIFont systemFontOfSize:9]].width;
            }
        }
        frame.origin.x = ceilf(self.bounds.size.width-(frame.size.width+16.0f));
        frame.origin.y = _statsView.hidden ? self.bounds.size.height - 20.0f : self.bounds.size.height - (45.0f + 29.0f);
        _commentView.frame = frame;
        [_commentView setNeedsDisplay];
    }
    
    [_headerView setNeedsDisplay];
    
    // date
    _dateLabel.text = [Util shortUserReadableTimeSinceDate:stamp.created];
    [_dateLabel sizeToFit];
    CGRect frame = _dateLabel.frame;
    frame.origin = CGPointMake(floorf(self.bounds.size.width - (frame.size.width+16.0f)), 10 - 2.5);
    _dateLabel.frame = frame;
    
    [_userImageView setupWithUser:stamp.user viewAction:YES];
    // user avatar
//    STProfileImageSize imageSize = STProfileImageSize96;
//    NSString* userImageURL = [Util profileImageURLForUser:stamp.user withSize:imageSize];
//    [self.userImageCancellation cancel];
//    self.userImageCancellation = nil;
//    self.userImageView.image = nil;
//    UIImage* image = nil;
//    if ([stamp.user.userID isEqual:[STStampedAPI sharedInstance].currentUser.userID]) {
//        image = [[STStampedAPI sharedInstance] currentUserImageForSize:imageSize];
//    }
//    if (!image) {
//        image = [[STImageCache sharedInstance] cachedImageForImageURL:userImageURL];
//    }
//    if (!image) {
//        self.userImageCancellation = [[STImageCache sharedInstance] imageForImageURL:userImageURL 
//                                                                         andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
//                                                                             NSAssert1(!cancellation.cancelled, @"Called when cancelled %@", userImageURL);
//                                                                             if (self.stamp == stamp) {
//                                                                                 self.userImageView.image = image;
//                                                                             }
//                                                                         }];
//    }
//    else {
//        self.userImageView.image = image;
//    }
    [self setNeedsDisplay];
}

- (void)toggleHightlighted:(BOOL)highlighted {
    if (highlighted) {
        _statsDots.fillColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.0f].CGColor;
        _statsDots.strokeColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor;
        _footerImageView.hidden = YES;
    }
    else {
        _statsDots.fillColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor;
        _statsDots.strokeColor = [UIColor colorWithRed:0.8509f green:0.8509f blue:0.8509f alpha:1.0f].CGColor;
    }
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
    [super setHighlighted:highlighted animated:animated];
    
    [self toggleHightlighted:highlighted];
    [_headerView setNeedsDisplay];
    [_commentView setNeedsDisplay];
    if (!highlighted) {
        _footerImageView.hidden = _statsView.hidden;
    }
    
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
    
    [self toggleHightlighted:selected];
    [_headerView setNeedsDisplay];
    [_commentView setNeedsDisplay];
    
}

+ (NSString*)cellIdentifier {
    return @"_inboxTableCell";
}

+ (CGFloat)heightForStamp:(id<STStamp>)stamp {
    if (stamp) {
        NSInteger count = stamp.previews.credits.count + stamp.previews.likes.count + stamp.previews.todos.count; //stamp.previews.comments.count;
        if (count > 0) {
            return 136.0f;
        }
    }
    return 92.0f;
}

+ (STCancellation*)prepareForStamp:(id<STStamp>)stamp withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
    NSArray* images = [STPreviewsView imagesForPreviewWithStamp:stamp andMaxRows:1];
    NSMutableArray* allImages = [NSMutableArray arrayWithObject:[Util profileImageURLForUser:stamp.user withSize:STProfileImageSize48]];
    [allImages addObjectsFromArray:images];
    return [STCancellation loadImages:allImages withCallback:block];
}


#pragma mark - STAvatarViewDelegate

- (void)stAvatarViewTapped:(STAvatarView*)view {
    
    if ([(id)delegate respondsToSelector:@selector(stStampCellAvatarTapped:)]) {
        [self.delegate stStampCellAvatarTapped:self];
    }
    
}


#pragma mark - Actions

- (void)longPress:(UILongPressGestureRecognizer*)gesture {
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
        
        STDetailTextCallout *callout = [[STDetailTextCallout alloc] initWithFrame:CGRectZero];
        callout.titleLabel.text = _title;
        callout.detailTitleLabel.text = _category;
        [self.window addSubview:callout];
        
        CGPoint point = [gesture locationInView:self];
        point.y -= 20.0f;
        [callout showCalloutFromPoint:[self convertPoint:point toView:self.window] animated:YES];
        [callout release];
        _callout = callout;
        
    } else if (gesture.state == UIGestureRecognizerStateChanged) {
        
        if (_callout) {
            
            CGPoint position = _callout.layer.position;
            position.x = [gesture locationInView:self].x;
            _callout.layer.position = position;
            
        }
        
    } else {
        
        if (_callout) {
            [_callout hide];
            _callout = nil;
        }
        
    }
    
    
}

@end

