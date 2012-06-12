//
//  STDetailTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import "STDetailTableCell.h"

@implementation STDetailTableCell
@synthesize detailTitleLabel=_detailTitleLabel;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {
        
        UIFont *font = [UIFont systemFontOfSize:11];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(0.0f, floorf((self.bounds.size.height-font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin;
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor clearColor];
        label.lineBreakMode = UILineBreakModeTailTruncation;
        [self addSubview:label];
        _detailTitleLabel = [label retain];
        [label release];
        
        self.titleLabel.font = [UIFont boldSystemFontOfSize:11];
        self.titleLabel.textColor = [UIColor colorWithWhite:0.349f alpha:1.0f];
        
    }
    return self;
}

- (void)dealloc {
    [_detailTitleLabel release], _detailTitleLabel=nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [_detailTitleLabel sizeToFit];
    
    CGRect frame = _detailTitleLabel.frame;
    frame.origin.x = floorf(self.bounds.size.width - (frame.size.width+30.0f));
    frame.size.width = MIN(self.bounds.size.width - 120.0f, frame.size.width);
    _detailTitleLabel.frame = frame;
    
    frame = self.titleLabel.frame;
    frame.size.width = MIN(frame.size.width, (self.bounds.size.width-(60.0f+_detailTitleLabel.frame.size.width)));
    self.titleLabel.frame = frame;
    
    
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];

}

@end
