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

@interface STStampCellAvatarView : UIImageView
@property(nonatomic,retain) NSURL *imageURL;
@end

@implementation STStampCell

@synthesize username=_username;
@synthesize subcategory=_subcategory;
@synthesize title=_title;
@synthesize category=_category;
@synthesize identifier=_identifier;
@synthesize commentCount=_commentCount;
@synthesize delegate;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
  if ((self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier])) {
      
      self.accessoryType = UITableViewCellAccessoryNone;
      
      CGFloat originY = 10.0f;
      UIImage *image = [UIImage imageNamed:@"stamp_cell_shadow_footer.png"];
      UIImageView *footer = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
      footer.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
      [self addSubview:footer];
      [footer release];
      CGRect frame = footer.frame;
      frame.size.width = self.frame.size.width;
      frame.origin.y = floorf(self.bounds.size.height-frame.size.height);
      footer.frame = frame;
      _footerImageView = footer;
      
      // user image view
      STStampCellAvatarView *imageView = [[STStampCellAvatarView alloc] initWithFrame:CGRectMake(11.0f, originY, 46.0f, 46.0f)];
      [self addSubview:imageView];
      _userImageView = imageView;
      [imageView release];
      
      UITapGestureRecognizer *tap = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(avatarTapped:)];
      [imageView addGestureRecognizer:tap];
      [tap release];
      
      UILongPressGestureRecognizer *longPress = [[UILongPressGestureRecognizer alloc] initWithTarget:self action:@selector(longPress:)];
      longPress.minimumPressDuration = 1.5f;
      [self addGestureRecognizer:longPress];
      [longPress release];
      
      // cell text
      STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:CGRectMake(68, originY, 200, 70.0f)];
      view.backgroundColor = [UIColor whiteColor];
      [self addSubview:view];
      [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
      
          BOOL highlighted = self.highlighted || self.selected;
          
          if (_username && _subcategory) {
              [highlighted ? [UIColor whiteColor] : [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f] setFill];
              UIFont *font = [UIFont boldSystemFontOfSize:10];
              CGSize size = [_username sizeWithFont:font];
              [_username drawInRect:CGRectMake(rect.origin.x, rect.origin.y, size.width, size.height) withFont:font lineBreakMode:UILineBreakModeTailTruncation];
              [_subcategory drawAtPoint:CGPointMake(size.width, rect.origin.y) withFont:[UIFont systemFontOfSize:10]];
          }
          
          if (_category) {
              if (_categoryImage) {
                  
                  if (highlighted) {
                      
                      CGContextSaveGState(ctx);
                      CGRect imageRect = CGRectMake(rect.origin.x, rect.size.height -  (56.0f+_categoryImage.size.height), _categoryImage.size.width, _categoryImage.size.height);
                      CGContextTranslateCTM(ctx, 0, rect.size.height);
                      CGContextScaleCTM(ctx, 1.0, -1.0);

                      [[UIColor whiteColor] setFill];
                      CGContextClipToMask(ctx, imageRect, _categoryImage.CGImage);

                      CGContextFillRect(ctx, imageRect);
                      CGContextRestoreGState(ctx);
                      
                  } else {
                      [_categoryImage drawAtPoint:CGPointMake(rect.origin.x, 56.0f)];
                  }
                  
              }
              [highlighted ? [UIColor whiteColor] : [UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f] setFill];
              [_category drawAtPoint:CGPointMake((_categoryImage!=nil) ? _categoryImage.size.width + 5.0f : 0.0f, 54.0f) withFont:[UIFont systemFontOfSize:10]];
          }
          
          if (_title) {
              
              UIFont *font = [UIFont stampedTitleLightFontWithSize:36];
              CGContextSetFillColorWithColor(ctx, [highlighted ? [UIColor whiteColor] : [UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:1.0f] CGColor]);
              
              CGFloat x = 0.0f;
              CGFloat y = 18.0f;
              BOOL _drawn = NO;

              for (NSInteger i = 0; i < _title.length; i++) {
                
                  BOOL truncate = (x > rect.size.width - 26.0f);
                  NSString *subString = truncate ? @"." : [_title substringWithRange:NSMakeRange(i, 1)];
                  CGSize size = [subString sizeWithFont:font];
                  CGPoint point = CGPointMake(x, y);
                  x += floorf(size.width + 1.5);

                  truncate = (x > rect.size.width - 26.0f);
                 
                  if (!_drawn && (truncate || i == _title.length-1)) {
                      _drawn = YES;
                      // draw stamp
                      if (_stampImage) {
                          
                          CGRect imageRect = CGRectMake(MIN(floorf(x - 7), rect.size.width-_stampImage.size.width), 17.0f, _stampImage.size.width, _stampImage.size.height);
                          if (self.highlighted) {
                              
                              CGContextSaveGState(ctx);
                              imageRect.origin.y = floorf(rect.size.height - (17.0f+_stampImage.size.height));
                              CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
                              CGContextScaleCTM(ctx, 1.0, -1.0);
                              [[UIColor whiteColor] setFill];
                              CGContextClipToMask(ctx, imageRect, _stampImage.CGImage);
                              CGContextFillRect(ctx, imageRect);
                              CGContextRestoreGState(ctx);
                              
                          } else {
                              
                              [_stampImage drawInRect:imageRect];
                              
                          }
                          
                      }
                      
                  }

                  [subString drawAtPoint:point withFont:font];

                  if (x >= rect.size.width) {
                      break;
                  }
                  
              }
         
          }

      }];
      _headerView = view;
      [view release];
      
      // date label
      UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
      label.font = [UIFont systemFontOfSize:10];
      label.textColor = [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f];
      label.highlightedTextColor = [UIColor whiteColor];
      label.backgroundColor = [UIColor whiteColor];
      [self addSubview:label];
      _dateLabel = label;
      [label release];
      
      STPreviewsView *previewsView = [[STPreviewsView alloc] initWithFrame:CGRectMake(69.0f, 95.0f, 0, 0)];
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
      STBlockUIView *commentView = [[STBlockUIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, 200, 30.0f)];
      commentView.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin;
      commentView.backgroundColor = [UIColor whiteColor];
      [self addSubview:commentView];
      [commentView setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
          
          BOOL highlighted = self.highlighted || self.selected;

          CGFloat offset = 0.0f;
          if (_commentCount > 0) {
              
              UIImage *image = [UIImage imageNamed:highlighted ? @"stamp_cell_comment_hi.png" : @"stamp_cell_comment.png"];
              [image drawAtPoint:CGPointMake(0, 1.0f)];

              offset += 12.0f;
              if (!_hasMedia) {

                  [highlighted ? [UIColor whiteColor] : [UIColor colorWithRed:0.521f green:0.635f blue:0.8f alpha:1.0f] setFill];
                  NSString *comments = [NSString stringWithFormat:@"%i", _commentCount];
                  CGFloat width = [[NSString stringWithFormat:@"%i", self.commentCount] sizeWithFont:[UIFont systemFontOfSize:9]].width;
                  UIFont *font = [UIFont systemFontOfSize:10];
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
    [_stampImage release], _stampImage = nil;
    
    _statsView = nil;
    _dateLabel = nil;

    [super dealloc];
    
}

- (void)setupWithStamp:(id<STStamp>)stamp {
    
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
    _subcategory =  [[NSString stringWithFormat:@" stamped a %@", stamp.entity.subcategory] copy];
    
    [_categoryImage release], _categoryImage=nil;
    _categoryImage = [[Util imageForCategory:stamp.entity.category] retain];
    
    [_stampImage release], _stampImage=nil;
    _stampImage = [[Util stampImageForUser:stamp.user withSize:STStampImageSize14] retain];
   
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
    _commentView.hidden = (_commentCount==0 && !_hasMedia);
    
    [_headerView setNeedsDisplay];
    [_commentView setNeedsDisplay];
    
    // date
    _dateLabel.text = [Util userReadableTimeSinceDate:stamp.created];
    [_dateLabel sizeToFit];
    frame = _dateLabel.frame;
    frame.origin = CGPointMake(floorf(self.bounds.size.width - (frame.size.width+16.0f)), 12);
    _dateLabel.frame = frame;
    
    // user avatar
    _userImageView.imageURL = [NSURL URLWithString:[Util profileImageURLForUser:stamp.user withSize:STProfileImageSize46]];
    
}

- (void)toggleHightlighted:(BOOL)highlighted {
    
    if (highlighted) {
        _statsDots.fillColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.0f].CGColor;
        _statsDots.strokeColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor;
        _footerImageView.hidden = YES;
    } else {
        _statsDots.fillColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor;
        _statsDots.strokeColor = [UIColor colorWithRed:0.8509f green:0.8509f blue:0.8509f alpha:1.0f].CGColor;
        _footerImageView.hidden = _statsView.hidden;
    }
    
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
    [super setHighlighted:highlighted animated:animated];
    
    [self toggleHightlighted:highlighted];
    [_headerView setNeedsDisplay];
    [_commentView setNeedsDisplay];
    
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
    NSMutableArray* allImages = [NSMutableArray arrayWithObject:[Util profileImageURLForUser:stamp.user withSize:STProfileImageSize46]];
    [allImages addObjectsFromArray:images];
    return [STCancellation loadImages:allImages withCallback:block];
}


#pragma mark - Actions

- (void)avatarTapped:(UITapGestureRecognizer*)gesture {
    
    if ([(id)delegate respondsToSelector:@selector(stStampCellAvatarTapped:)]) {
        [self.delegate stStampCellAvatarTapped:self];
    }
    
}

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


#pragma mark - STStampCellAvatarView

@implementation STStampCellAvatarView
@synthesize imageURL=_imageURL;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.userInteractionEnabled = YES;
        self.backgroundColor = [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f];
        self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
        self.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
        self.layer.shadowRadius = 1.0f;
        self.layer.shadowOpacity = 0.2f;
        self.layer.borderColor = [UIColor whiteColor].CGColor;
        self.layer.borderWidth = 1.0f;
    }
    return self;
}

- (void)dealloc {
    [_imageURL release], _imageURL=nil;
    [super dealloc];
}

- (void)setImageURL:(NSURL *)imageURL {
    if (_imageURL && [_imageURL isEqual:imageURL]) return;
    [_imageURL release], _imageURL=nil;
    _imageURL = [imageURL retain];
    
    self.image = nil;
    [[ImageLoader sharedLoader] imageForURL:_imageURL completion:^(UIImage *image, NSURL *url) {
        if ([_imageURL isEqual:url]) {
            self.image = image;
        }
    }];
    
}

@end
