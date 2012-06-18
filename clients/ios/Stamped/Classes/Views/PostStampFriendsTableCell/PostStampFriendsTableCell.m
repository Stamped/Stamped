//
//  PostStampFriendsTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import "PostStampFriendsTableCell.h"
#import "PostStampFriendView.h"
#import "NSStringHelper.h"
#import <CoreText/CoreText.h>

#define kMaxItems 5

@implementation PostStampFriendsTableCell
@synthesize delegate;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"post_stamp_stampedby_icon.png"]];
        [self addSubview:imageView];
        CGRect frame = imageView.frame;
        frame.origin.x = 20.0f;
        frame.origin.y = 11.0f;
        imageView.frame = frame;
        [imageView release];

        CATextLayer *textLayer = [CATextLayer layer];
        textLayer.contentsScale = [[UIScreen mainScreen] scale];
        [self.layer addSublayer:textLayer];
        _titleLayer = textLayer;
        
        NSMutableArray *array = [[NSMutableArray alloc] initWithCapacity:6];
        for (NSInteger i = 0; i < 6; i++) {
            PostStampFriendView *view = [[PostStampFriendView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, 48.0f, 60.0f)];
            [view addTarget:self action:@selector(friendSelected:) forControlEvents:UIControlEventTouchUpInside];
            [array addObject:view];
            [view release];
        }
        _userViews = [array retain];
        [array release];
        
    }
    return self;
}

- (void)dealloc {
    [_userViews release], _userViews=nil;
    [super dealloc];
}


#pragma mark - Setters

- (void)setupWithStampedBy:(id<STStampedBy>)stampedBy andStamp:(id<STStamp>)stamp {
    
    NSString *ordinalText = [NSString ordinalString:[NSNumber numberWithInteger:stampedBy.friends.count.integerValue + 1]];
    NSString *title = [NSString stringWithFormat:@"You're the %@ of your friends to stamp this.", ordinalText];
    
    UIColor *textColor = [UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f];
    UIColor *boldTextColor = [UIColor colorWithRed:0.349f green:0.349f blue:0.349f alpha:1.0f];
    CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"HelveticaNeue" : (CFStringRef)@"Helvetica", 11, NULL);
    CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
    NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)boldTextColor.CGColor, kCTForegroundColorAttributeName, nil];
    
    NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)textColor.CGColor, kCTForegroundColorAttributeName, nil];
    
    CFRelease(ctFont);
    CFRelease(boldFont);
    
    NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:title attributes:defaultStyle];
    [string setAttributes:boldStyle range:[string.string rangeOfString:ordinalText]];
    
    [defaultStyle release];
    [boldStyle release];
    
    CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString( (CFMutableAttributedStringRef) string); 
    CGSize size = CTFramesetterSuggestFrameSizeWithConstraints(framesetter, CFRangeMake(0, 0), NULL, CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX), NULL);
    CFRelease(framesetter);
    
    _titleLayer.string = string;
    [string release];
    _titleLayer.frame = CGRectMake(42.0f, 12.0f, size.width, size.height);
    
    if (!stampedBy || !stamp) return;

    NSMutableArray *stampPreviews = [NSMutableArray array];
    for (id<STStampPreview> stampPreview in stampedBy.friends.stampPreviews) {
        [stampPreviews addObject:stampPreview];
        if (stampPreviews.count > 6) {
            break;
        }
    }

    CGFloat originX = 16.0f;
    CGFloat originY = 36.0f;
    
    NSInteger index = stampedBy.friends.count.integerValue;
    NSInteger count = MIN(index, kMaxItems);
    NSInteger offset = index - count;
    for (NSInteger i = 0; i < count; i++) {
      
        id<STStamp> aStamp = [stampPreviews objectAtIndex:i];
        PostStampFriendView *view = [_userViews objectAtIndex:i];
        [view setupWithUser:aStamp.user index:offset + (i+1)];
        CGRect frame = view.frame;
        frame.origin = CGPointMake(originX, originY);
        [self addSubview:view];
        view.frame = frame;
        originX += 48;
        index--;
        
    }
    
    PostStampFriendView *view = [_userViews lastObject];
    [view setupWithUser:stamp.user index:stampedBy.friends.count.integerValue + 1];
    CGRect frame = view.frame;
    frame.origin = CGPointMake(originX, originY);
    [self addSubview:view];
    view.frame = frame;
    
}

- (void)showShadow:(BOOL)show {
    
    if (show) {
        
        if (!_shadowView) {
            UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"post_stamp_keyline_shadow.png"]];
            [self addSubview:imageView];
            
            CGRect frame = imageView.frame;
            frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
            imageView.frame = frame;
            [imageView release];
            _shadowView = imageView;
        }
        
        if (_borderView) {
            [_borderView removeFromSuperview];
            _borderView = nil;
        }
        
    } else {
        
        if (!_borderView) {
            UIView *view = [[UIView alloc] initWithFrame:CGRectMake(5.0f, 0.0f, self.bounds.size.width-10.0f, 1.0f)];
            view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.1f];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
            [self addSubview:view];
            _borderView = view;
            [view release];
        }
        
        if (_shadowView) {
            [_shadowView removeFromSuperview];
            _shadowView = nil;
        }
        
    }
    
    
}


#pragma mark - Actions

- (void)friendSelected:(PostStampFriendView*)view {
    
    if ([(id)delegate respondsToSelector:@selector(postStampFriendTableCell:selectedUser:)]) {
        [self.delegate postStampFriendTableCell:self selectedUser:view.user];
    }
    
}


@end
