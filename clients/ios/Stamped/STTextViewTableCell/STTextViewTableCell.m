//
//  STTextViewTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/19/12.
//
//

#import "STTextViewTableCell.h"

@interface STTextViewTableCell () <UITextViewDelegate>
@end

@implementation STTextViewTableCell
@synthesize textView = _textView;
@synthesize titleLabel = _titleLabel;
@synthesize delegate;
@synthesize lastHeight;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {

        self.selectionStyle = UITableViewCellSelectionStyleNone;
        
        UIView *background = [[UIView alloc] initWithFrame:CGRectZero];
        self.backgroundView = background;
        [background release];
        
        UIImage *image = [UIImage imageNamed:@"signup_text_field_bg.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:(image.size.height/2)]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        imageView.frame = CGRectMake(10.0f, 0.0f, floorf(self.bounds.size.width - 20.0f), image.size.height);
        [self addSubview:imageView];
        [imageView release];
        
        UIFont *font = [UIFont systemFontOfSize:13];
        UITextView *textView = [[UITextView alloc] initWithFrame:CGRectMake(20.0f, 4.0f, floorf(self.bounds.size.width - 40.0f), 20.0f)];
        textView.autoresizingMask = UIViewAutoresizingFlexibleHeight;
        textView.scrollEnabled = NO;
        textView.delegate = (id<UITextViewDelegate>)self;
        textView.font = font;
        textView.textColor = [UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:1.0f];
        textView.backgroundColor = [UIColor clearColor];
        [self addSubview:textView];
        _textView = [textView retain];
        [textView release];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textAlignment = UITextAlignmentRight;
        label.userInteractionEnabled = NO;
        label.adjustsFontSizeToFitWidth = YES;
        label.minimumFontSize = 9;
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleRightMargin;
        label.backgroundColor = [UIColor clearColor];
        label.font = [UIFont systemFontOfSize:12];
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        [imageView addSubview:label];
        _titleLabel = [label retain];
        [label release];
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [self addGestureRecognizer:gesture];
        [gesture release];
        
        
    }
    return self;
}

- (void)dealloc {
    self.textView = nil;
    self.titleLabel = nil;
    self.delegate = nil;
    [super dealloc];
}


#pragma mark - Layout

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [self.titleLabel sizeToFit];
    CGRect frame = self.titleLabel.frame;
    
    frame.size.width = MIN(frame.size.width, 94.0f);
    if (self.titleLabel.textAlignment == UITextAlignmentRight) {
        frame.origin.x = 100 - frame.size.width;
    } else {
        frame.origin.x = 20.0f;
    }
    frame.origin.y = floorf((44.0f-frame.size.height)/2);
    self.titleLabel.frame = frame;
    
    frame = self.textView.frame;
    frame.origin.x = CGRectGetMaxX(self.titleLabel.frame) + 12.0f;
    frame.size.width = floorf(self.bounds.size.width - (frame.origin.x+30.0f));
    self.textView.frame = frame;
            
}

+ (CGFloat)heightForText:(NSString*)text {
    
    CGSize size = [text sizeWithFont:[UIFont systemFontOfSize:13] constrainedToSize:CGSizeMake(162, CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];

    if (size.height > 16 ||  (text.length > 0 && [text characterAtIndex:text.length-1] == '\n')) {
        size.height += 32.0f;
    }
        
    size.height += 16;
    return MAX(48, size.height);
    
}

- (CGFloat)height {
    
    return [[self class] heightForText:self.textView.text];
    
}


#pragma mark - Gesture

- (void)tapped:(UITapGestureRecognizer*)gesture {
    [self.textView becomeFirstResponder];
}


#pragma mark - UIGestureRecognizerDelegate

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    return !CGRectContainsPoint(self.textView.frame, [gestureRecognizer locationInView:self]);
}


#pragma mark - UITextViewDelegate


- (void)textViewDidBeginEditing:(UITextView *)textView {
    if ([(id)delegate respondsToSelector:@selector(stTextViewTableCellDidBeginEditing:)]) {
        [self.delegate stTextViewTableCellDidBeginEditing:self];
    }
}

- (void)textViewDidEndEditing:(UITextView *)textView {
    if ([(id)delegate respondsToSelector:@selector(stTextViewTableCellDidEndEditing:)]) {
        [self.delegate stTextViewTableCellDidEndEditing:self];
    }
}

- (void)textViewDidChange:(UITextView *)textView {
    NSLog(@"textChanged");
    if ([(id)delegate respondsToSelector:@selector(stTextViewTableCell:textChanged:)]) {
        [self.delegate stTextViewTableCell:self textChanged:self.textView];
    }
    
    CGFloat height = MAX(self.textView.contentSize.height + 16.0f, 48.0f);
    if (self.lastHeight != height) {
        NSLog(@"heightChanged");
        if ([(id)delegate respondsToSelector:@selector(stTextViewTableCell:heightChangedFrom:to:)]) {
            [self.delegate stTextViewTableCell:self heightChangedFrom:self.lastHeight to:height];
        }
        
    }
    
    self.lastHeight = height;
    
}


@end
